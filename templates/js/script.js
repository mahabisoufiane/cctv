const API_URL = 'http://127.0.0.1:5000';

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // Load pricing data
    loadPricingData();
    setupFormSubmit();
    setupPriceCalculation();

    // Close mobile menu when clicking links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
        });
    });
});

// Load data from backend
async function loadPricingData() {
    try {
        const response = await fetch(`${API_URL}/data`);
        const data = await response.json();

        // Populate locations
        const locationSelect = document.getElementById('location');
        data.locations.forEach(loc => {
            const option = document.createElement('option');
            option.value = loc.id;
            option.textContent = loc.name;
            locationSelect.appendChild(option);
        });

        // Populate resolutions
        const resolutionSelect = document.getElementById('resolution');
        data.resolutions.forEach(res => {
            const option = document.createElement('option');
            option.value = res.resolution;
            option.textContent = `${res.resolution} - $${res.base_price}`;
            resolutionSelect.appendChild(option);
        });

        // Populate difficulties
        const difficultySelect = document.getElementById('difficulty');
        data.difficulties.forEach(diff => {
            const option = document.createElement('option');
            option.value = diff.level;
            option.textContent = `${diff.level}`;
            difficultySelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Update camera count display
function setupPriceCalculation() {
    const cameraSlider = document.getElementById('cameras');
    const cameraCount = document.getElementById('cameraCount');

    if (cameraSlider) {
        cameraSlider.addEventListener('input', () => {
            cameraCount.textContent = cameraSlider.value;
        });
    }
}

// Calculate price
async function calculatePrice() {
    const location = document.getElementById('location').value;
    const cameras = document.getElementById('cameras').value;
    const resolution = document.getElementById('resolution').value;
    const difficulty = document.getElementById('difficulty').value;

    if (!location || !cameras || !resolution || !difficulty) {
        alert('❌ Please fill all fields');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/calculate-price`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                camera_count: parseInt(cameras),
                resolution: resolution,
                location_id: parseInt(location),
                difficulty_level: difficulty
            })
        });

        const result = await response.json();

        if (response.ok) {
            document.getElementById('totalPrice').textContent = result.total_price.toFixed(2);
            document.getElementById('totalPrice2').textContent = result.total_price.toFixed(2);
            document.getElementById('cameraCost').textContent = result.breakdown.camera_cost.toFixed(2);
            document.getElementById('laborCost').textContent = result.breakdown.labor_cost.toFixed(2);
            document.getElementById('travelFee').textContent = result.breakdown.travel_fee.toFixed(2);
            document.getElementById('priceResult').classList.remove('hidden');

            // Scroll to result
            document.getElementById('priceResult').scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('❌ Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error calculating price:', error);
        alert('❌ Error calculating price');
    }
}

// Setup form submission
function setupFormSubmit() {
    const form = document.getElementById('quoteForm');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            service: document.getElementById('service').value,
            message: document.getElementById('message').value,
            location_id: parseInt(document.getElementById('location').value) || null,
            camera_count: parseInt(document.getElementById('cameras').value) || null,
            resolution: document.getElementById('resolution').value,
            difficulty_level: document.getElementById('difficulty').value,
            estimated_price: parseFloat(document.getElementById('totalPrice').textContent) || 0
        };

        try {
            const response = await fetch(`${API_URL}/quote`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            const messageDiv = document.getElementById('formMessage');

            if (result.success) {
                messageDiv.className = 'form-message success';
                messageDiv.innerHTML = '✅ <strong>Quote submitted successfully!</strong><br>Check your email for confirmation.';
                form.reset();
                document.getElementById('priceResult').classList.add('hidden');
                
                setTimeout(() => {
                    messageDiv.textContent = '';
                    messageDiv.classList.remove('success');
                }, 5000);
            } else {
                messageDiv.className = 'form-message error';
                messageDiv.textContent = '❌ Error: ' + JSON.stringify(result.errors || result.message);
            }
        } catch (error) {
            console.error('Error submitting quote:', error);
            const messageDiv = document.getElementById('formMessage');
            messageDiv.className = 'form-message error';
            messageDiv.textContent = '❌ Error submitting quote: ' + error.message;
        }
    });
}
