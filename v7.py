# verfication page Update

from flask import Flask, request, jsonify, redirect, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import json
from datetime import datetime

app = Flask(__name__)

# Initialize Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Initialize Flask-Limiter for rate-limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["2 per minute"]
)

# Middleware to log IP addresses before each request
@app.before_request
def log_ip():
    ip = request.remote_addr
    print(f"User IP: {ip}")

    # Log user data to JSON
    user_data = {
        "ip": ip,
        "timestamp": datetime.utcnow().isoformat()
    }
    log_user_data(user_data)

def log_user_data(data):
    try:
        with open('user-data.json', 'a') as f:
            json.dump(data, f)
            f.write('\n')  # Write each record on a new line
    except Exception as e:
        print(f"Error logging user data: {e}")

# Rate-limiting handler for too many requests
@app.errorhandler(429)
def ratelimit_error(e):
    ip = request.remote_addr
    print(f"IP {ip} exceeded the rate limit. Moving to human verification.")
    return redirect('/human-verification')

# Route for human verification page
@app.route('/human-verification', methods=['GET'])
def human_verification():
    return render_template_string('''
       <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Human Verification</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        
        .verification-container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            width: 300px;
            text-align: center;
        }
        
        h2 {
            margin-bottom: 20px;
        }
        
        p {
            margin-bottom: 20px;
            color: #555;
        }
        
        .verification-form {
            margin-top: 20px;
        }
        
        .checkbox-container {
            display: block;
            position: relative;
            padding-left: 35px;
            margin-bottom: 15px;
            cursor: pointer;
            font-size: 18px;
            user-select: none;
        }
        
        .checkbox-container input {
            position: absolute;
            opacity: 0;
            cursor: pointer;
        }
        
        .checkmark {
            position: absolute;
            top: 0;
            left: 0;
            height: 20px;
            width: 20px;
            background-color: #eee;
            border-radius: 4px;
        }
        
        .checkbox-container input:checked ~ .checkmark {
            background-color: #0084ff;
        }
        
        .checkmark:after {
            content: "";
            position: absolute;
            display: none;
        }
        
        .checkbox-container input:checked ~ .checkmark:after {
            display: block;
        }
        
        .checkbox-container .checkmark:after {
            left: 7px;
            top: 3px;
            width: 5px;
            height: 10px;
            border: solid white;
            border-width: 0 3px 3px 0;
            transform: rotate(45deg);
        }
        
        .math-question {
            margin-top: 10px;
            text-align: left;
        }
        
        .math-question label {
            font-size: 16px;
        }
        
        .math-question input {
            width: 100%;
            padding: 8px;
            margin-top: 5px;
            border-radius: 4px;
            border: 1px solid #ccc;
        }
        
        button {
            background-color: blue;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
            width: 100%;
        }
        
        button:hover {
            background-color: #0084ff;
        }
        
        #resultMessage {
            margin-top: 20px;
            font-size: 16px;
            color: red;
        }
        
    </style>
</head>
<body>
    <div class="verification-container">
        <h2>Human Verification</h2>
        <p>Before proceeding, please verify that you are a human.</p>

        <div class="verification-form">
            <!-- Simple Checkbox for Human Verification -->
            <label class="checkbox-container">
                <input type="checkbox" id="verifyCheckbox">
                I am not a robot
                <span class="checkmark"></span>
            </label>

            <!-- OR a simple math question -->
            <div class="math-question">
                <label for="mathAnswer">What is 3 + 3 ?</label>
                <input type="number" id="mathAnswer" placeholder="Enter your answer">
            </div>

            <button id="verifyBtn">Verify</button>
            <p id="resultMessage"></p>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', () => {
        const verifyBtn = document.getElementById('verifyBtn');
        const verifyCheckbox = document.getElementById('verifyCheckbox');
        const mathAnswer = document.getElementById('mathAnswer');
        const resultMessage = document.getElementById('resultMessage');

        // Human verification logic
        verifyBtn.addEventListener('click', () => {
            const answer = mathAnswer.value;
            
            // Check if checkbox is checked or the correct math answer is given
            if (verifyCheckbox.checked || answer === "6") { // Correct answer is 6, not 8
                resultMessage.style.color = "#0084ff";
                resultMessage.textContent = "Verification successful! You are human.";

                // Redirect to another page after successful verification
                setTimeout(() => {
                    window.location.href = "/verify"; // Redirect to Flask verification route
                }, 1000);  // Delay to show the success message before redirect
            } else {
                resultMessage.style.color = "red";
                resultMessage.textContent = "Verification failed. Please try again.";
            }
        });
    });
    </script>
</body>
</html>
    ''')

# Route to handle verification after human check
@app.route('/verify', methods=['POST', 'GET'])
def verify():
    # Render the homepage with a success flag
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Netflix Clone</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            margin: 0;
            font-family: 'Roboto', sans-serif;
            background-color: #141414;
            color: white;
        }

        /* Top Navigation Bar */
        .navbar {
            background-color: #141414;
            padding: 15px 30px;
            position: fixed;
            width: 100%;
            z-index: 10;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .navbar .logo {
            font-size: 28px;
            font-weight: bold;
            color: #e50914;
        }

        .navbar ul {
            list-style: none;
            display: flex;
        }

        .navbar ul li {
            margin-left: 20px;
        }

        .navbar ul li a {
            color: white;
            text-decoration: none;
            font-weight: 500;
        }

        /* Hero Section */
        .hero {
            position: relative;
            height: 80vh;
            background: url('https://images.unsplash.com/photo-1517602302552-471fe67acf62') no-repeat center center/cover;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        .hero::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
        }

        .hero-content {
            position: relative;
            z-index: 1;
            color: white;
        }

        .hero-content h1 {
            font-size: 48px;
            margin-bottom: 20px;
        }

        .hero-content p {
            font-size: 18px;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.5;
        }

        /* Content Section */
        .content-section {
            padding: 40px 30px;
        }

        .content-section h2 {
            font-size: 24px;
            margin-bottom: 20px;
        }

        .carousel {
            display: flex;
            overflow-x: scroll;
            padding-bottom: 20px;
        }

        .carousel::-webkit-scrollbar {
            display: none;
        }

        .carousel-item {
            min-width: 200px;
            margin-right: 10px;
            background-color: #333;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
        }

        .carousel-item img {
            width: 100%;
            height: auto;
        }

        /* Popup */
        .popup {
            display: none;
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background-color: #0084ff;
            color: white;
            padding: 15px 25px;
            border-radius: 5px;
            z-index: 100;
            font-size: 16px;
        }

        .popup.show {
            display: block;
        }

        /* Footer */
        footer {
            background-color: #141414;
            padding: 20px;
            text-align: center;
            color: #aaa;
            font-size: 14px;
        }
    </style>
</head>
<body>

    <!-- Top Navigation -->
    <div class="navbar">
        <div class="logo">Netflix</div>
        <ul>
            <li><a href="#">Home</a></li>
            <li><a href="#">TV Shows</a></li>
            <li><a href="#">Movies</a></li>
            <li><a href="#">New & Popular</a></li>
            <li><a href="#">My List</a></li>
        </ul>
    </div>

    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-content">
            <h1>Featured Movie Title</h1>
            <p>Watch the latest and greatest movies and TV shows from around the world. Join now to start streaming instantly.</p>
        </div>
    </section>

    <!-- Content Section -->
    <section class="content-section">
        <h2>Trending Now</h2>
        <div class="carousel">
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+1" alt="Movie 1">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+2" alt="Movie 2">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+3" alt="Movie 3">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+4" alt="Movie 4">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+5" alt="Movie 5">
            </div>
        </div>
    </section>

    <!-- Popular Section -->
    <section class="content-section">
        <h2>Popular on Netflix</h2>
        <div class="carousel">
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+6" alt="Movie 6">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+7" alt="Movie 7">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+8" alt="Movie 8">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+9" alt="Movie 9">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+10" alt="Movie 10">
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer>
        Netflix Clone &copy; 2024 | Made with ♥ for learning
    </footer>

    <!-- Popup Message -->
    <div id="popup" class="popup">Verification successful! You are now allowed to access the site.</div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const popup = document.getElementById('popup');
            // Show the popup
            popup.classList.add('show');

            // Hide the popup after 3 seconds
            setTimeout(() => {
                popup.classList.remove('show');
            }, 3000);
        });
    </script>

</body>
</html>
    ''')


# Main route (home page)
@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Netflix Clone</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            margin: 0;
            font-family: 'Roboto', sans-serif;
            background-color: #141414;
            color: white;
        }

        /* Top Navigation Bar */
        .navbar {
            background-color: #141414;
            padding: 15px 30px;
            position: fixed;
            width: 100%;
            z-index: 10;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .navbar .logo {
            font-size: 28px;
            font-weight: bold;
            color: #e50914;
        }

        .navbar ul {
            list-style: none;
            display: flex;
        }

        .navbar ul li {
            margin-left: 20px;
        }

        .navbar ul li a {
            color: white;
            text-decoration: none;
            font-weight: 500;
        }

        /* Hero Section */
        .hero {
            position: relative;
            height: 80vh;
            background: url('https://images.unsplash.com/photo-1517602302552-471fe67acf62') no-repeat center center/cover;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        .hero::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
        }

        .hero-content {
            position: relative;
            z-index: 1;
            color: white;
        }

        .hero-content h1 {
            font-size: 48px;
            margin-bottom: 20px;
        }

        .hero-content p {
            font-size: 18px;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.5;
        }

        /* Content Section */
        .content-section {
            padding: 40px 30px;
        }

        .content-section h2 {
            font-size: 24px;
            margin-bottom: 20px;
        }

        .carousel {
            display: flex;
            overflow-x: scroll;
            padding-bottom: 20px;
        }

        .carousel::-webkit-scrollbar {
            display: none;
        }

        .carousel-item {
            min-width: 200px;
            margin-right: 10px;
            background-color: #333;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
        }

        .carousel-item img {
            width: 100%;
            height: auto;
        }

        /* Footer */
        footer {
            background-color: #141414;
            padding: 20px;
            text-align: center;
            color: #aaa;
            font-size: 14px;
        }
    </style>
</head>
<body>

    <!-- Top Navigation -->
    <div class="navbar">
        <div class="logo">Netflix</div>
        <ul>
            <li><a href="#">Home</a></li>
            <li><a href="#">TV Shows</a></li>
            <li><a href="#">Movies</a></li>
            <li><a href="#">New & Popular</a></li>
            <li><a href="#">My List</a></li>
        </ul>
    </div>

    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-content">
            <h1>Featured Movie Title</h1>
            <p>Watch the latest and greatest movies and TV shows from around the world. Join now to start streaming instantly.</p>
        </div>
    </section>

    <!-- Content Section -->
    <section class="content-section">
        <h2>Trending Now</h2>
        <div class="carousel">
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+1" alt="Movie 1">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+2" alt="Movie 2">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+3" alt="Movie 3">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+4" alt="Movie 4">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+5" alt="Movie 5">
            </div>
        </div>
    </section>

    <section class="content-section">
        <h2>Popular on Netflix</h2>
        <div class="carousel">
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+6" alt="Movie 6">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+7" alt="Movie 7">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+8" alt="Movie 8">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+9" alt="Movie 9">
            </div>
            <div class="carousel-item">
                <img src="https://via.placeholder.com/200x300.png?text=Movie+10" alt="Movie 10">
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer>
        Netflix Clone &copy; 2024 | Made with ♥ for learning
    </footer>

</body>
</html>

''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
