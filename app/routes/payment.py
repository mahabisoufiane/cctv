from flask import jsonify, request, current_app
from app.routes import payment_bp
from app.models import QuoteRequest
from app.models_extended import Payment, Invoice
from app import db
from datetime import datetime, timedelta


# ============================================================================
# PAYMENT GATEWAY INTEGRATIONS
# ============================================================================

# Mock gateway responses (replace with actual API calls)
class PaymentGateway:
    """Abstract payment gateway interface"""
    
    @staticmethod
    def create_session(amount, currency, metadata):
        """Create payment session"""
        raise NotImplementedError
    
    @staticmethod
    def verify_payment(transaction_id):
        """Verify payment status"""
        raise NotImplementedError


class StripeGateway(PaymentGateway):
    """Stripe payment integration"""
    
    @staticmethod
    def create_session(amount, currency, metadata):
        try:
            import stripe
            stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {'name': 'CCTV Installation'},
                        'unit_amount': int(amount * 100)
                    },
                    'quantity': 1
                }],
                mode='payment',
                success_url=current_app.config.get('APP_URL') + '/payment/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=current_app.config.get('APP_URL') + '/payment/cancel',
                metadata=metadata
            )
            return {'success': True, 'session_id': session.id, 'url': session.url}
        except Exception as e:
            current_app.logger.error(f"Stripe error: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def verify_payment(session_id):
        try:
            import stripe
            stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
            
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'success': True,
                'status': session.payment_status,
                'amount': session.amount_total / 100
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class PayPalGateway(PaymentGateway):
    """PayPal payment integration"""
    
    @staticmethod
    def create_session(amount, currency, metadata):
        # TODO: Implement PayPal API
        return {'success': False, 'error': 'PayPal integration coming soon'}
    
    @staticmethod
    def verify_payment(transaction_id):
        # TODO: Implement PayPal verification
        return {'success': False, 'error': 'PayPal verification coming soon'}


class MarocTelecomGateway(PaymentGateway):
    """Maroc Telecom (OrangeMoney) integration for Morocco"""
    
    @staticmethod
    def create_session(amount, currency, metadata):
        # TODO: Implement Maroc Telecom API
        return {'success': False, 'error': 'Maroc Telecom integration coming soon'}
    
    @staticmethod
    def verify_payment(transaction_id):
        # TODO: Implement Maroc Telecom verification
        return {'success': False, 'error': 'Maroc Telecom verification coming soon'}


# ============================================================================
# PAYMENT ENDPOINTS
# ============================================================================

@payment_bp.route('/create-payment', methods=['POST'])
def create_payment():
    """Initiate payment for a quote"""
    try:
        data = request.get_json()
        quote_id = data.get('quote_id')
        payment_method = data.get('payment_method', 'stripe')  # stripe, paypal, cash, bank
        
        quote = QuoteRequest.query.get(quote_id)
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404
        
        # Check if payment already exists
        existing_payment = Payment.query.filter_by(quote_id=quote_id).first()
        if existing_payment:
            return jsonify({
                'success': False,
                'error': 'Payment already exists for this quote',
                'payment_id': existing_payment.id
            }), 400
        
        # Create payment record
        payment = Payment(
            quote_id=quote_id,
            amount=data.get('amount', 0),
            currency='MAD',
            payment_method=payment_method,
            due_date=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # If online payment, create gateway session
        if payment_method in ['stripe', 'paypal', 'maroc_telecom']:
            if payment_method == 'stripe':
                gateway_response = StripeGateway.create_session(
                    amount=payment.amount,
                    currency='MAD',
                    metadata={'quote_id': quote_id, 'payment_id': payment.id}
                )
            elif payment_method == 'paypal':
                gateway_response = PayPalGateway.create_session(
                    amount=payment.amount,
                    currency='MAD',
                    metadata={'quote_id': quote_id, 'payment_id': payment.id}
                )
            else:  # maroc_telecom
                gateway_response = MarocTelecomGateway.create_session(
                    amount=payment.amount,
                    currency='MAD',
                    metadata={'quote_id': quote_id, 'payment_id': payment.id}
                )
            
            if gateway_response['success']:
                payment.payment_gateway = payment_method
                db.session.commit()
                return jsonify({
                    'success': True,
                    'payment_id': payment.id,
                    'session_id': gateway_response.get('session_id'),
                    'payment_url': gateway_response.get('url'),
                    'message': f'Payment session created using {payment_method}'
                }), 201
            else:
                db.session.delete(payment)
                db.session.commit()
                return jsonify({
                    'success': False,
                    'error': gateway_response.get('error', 'Payment gateway error')
                }), 500
        else:
            # Manual payment (cash, bank transfer)
            return jsonify({
                'success': True,
                'payment_id': payment.id,
                'status': 'pending',
                'message': f'Payment record created. Please arrange {payment_method} payment.',
                'amount': payment.amount,
                'currency': payment.currency,
                'due_date': payment.due_date.isoformat()
            }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Payment creation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/verify-payment', methods=['POST'])
def verify_payment():
    """Verify payment completion"""
    try:
        data = request.get_json()
        payment_id = data.get('payment_id')
        session_id = data.get('session_id')
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'success': False, 'error': 'Payment not found'}), 404
        
        # Verify with gateway
        if payment.payment_gateway == 'stripe':
            result = StripeGateway.verify_payment(session_id)
        elif payment.payment_gateway == 'paypal':
            result = PayPalGateway.verify_payment(session_id)
        else:
            result = MarocTelecomGateway.verify_payment(session_id)
        
        if result['success'] and result['status'] == 'paid':
            payment.status = 'completed'
            payment.paid_at = datetime.utcnow()
            payment.transaction_id = session_id
            
            quote = payment.quote
            quote.status = 'converted'
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Payment verified',
                'payment': payment.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Payment verification failed')
            }), 400
    
    except Exception as e:
        current_app.logger.error(f"Payment verification error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/payment/<int:payment_id>/refund', methods=['POST'])
def refund_payment(payment_id):
    """Refund a payment"""
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'success': False, 'error': 'Payment not found'}), 404
        
        if payment.status != 'completed':
            return jsonify({
                'success': False,
                'error': f"Cannot refund payment with status: {payment.status}"
            }), 400
        
        # Process refund with gateway
        if payment.payment_gateway == 'stripe':
            # TODO: Implement Stripe refund
            pass
        
        payment.status = 'refunded'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment refunded',
            'payment': payment.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/payment/<int:payment_id>/status')
def get_payment_status(payment_id):
    """Get payment status"""
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'success': False, 'error': 'Payment not found'}), 404
        
        return jsonify({
            'success': True,
            'payment': payment.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# INVOICE ENDPOINTS
# ============================================================================

@payment_bp.route('/invoice/<int:quote_id>/generate', methods=['POST'])
def generate_invoice(quote_id):
    """Generate PDF invoice"""
    try:
        quote = QuoteRequest.query.get(quote_id)
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404
        
        # Check if invoice already exists
        existing_invoice = Invoice.query.filter_by(quote_id=quote_id).first()
        if existing_invoice:
            return jsonify({
                'success': True,
                'invoice': existing_invoice.to_dict()
            }), 200
        
        data = request.get_json()
        
        # Calculate totals
        subtotal = data.get('subtotal', 0)
        tax_rate = 0.2  # 20% TVA in Morocco
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount
        
        invoice = Invoice(
            quote_id=quote_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            due_date=datetime.utcnow() + timedelta(days=30),
            status='issued'
        )
        
        invoice.invoice_number = invoice.generate_invoice_number()
        
        db.session.add(invoice)
        db.session.commit()
        
        # TODO: Generate PDF
        # invoice.pdf_url = generate_pdf_invoice(invoice)
        # db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Invoice {invoice.invoice_number} generated',
            'invoice': invoice.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Invoice generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/invoice/<int:invoice_id>/pdf')
def download_invoice_pdf(invoice_id):
    """Download invoice as PDF"""
    try:
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({'success': False, 'error': 'Invoice not found'}), 404
        
        # TODO: Generate and serve PDF
        # from flask import send_file
        # return send_file(invoice.pdf_url, as_attachment=True)
        
        return jsonify({
            'success': True,
            'message': 'PDF generation not yet implemented',
            'invoice': invoice.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/invoice/<int:invoice_id>')
def get_invoice(invoice_id):
    """Get invoice details"""
    try:
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({'success': False, 'error': 'Invoice not found'}), 404
        
        return jsonify({
            'success': True,
            'invoice': invoice.to_dict(),
            'quote': invoice.quote.to_dict(),
            'payment': invoice.payment.to_dict() if invoice.payment else None
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
