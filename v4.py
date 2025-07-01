from flask import Flask, request, jsonify, redirect, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import json
from datetime import datetime

app = Flask(__name__)

# Initialize Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Initialize Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["2 per minute"]
)

# Middleware to log IP addresses
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

# Rate limiting handler
@app.errorhandler(429)
def ratelimit_error(e):
    ip = request.remote_addr
    print(f"IP {ip} exceeded the rate limit. Moving to human verification.")
    return redirect('/human-verification')

# Human verification page
@app.route('/human-verification', methods=['GET'])
def human_verification():
    return render_template_string('''
        <h1>Human Verification Required</h1>
        <p>To continue, please complete the CAPTCHA below.</p>
        <form action="/verify" method="POST">
            <!-- Include CAPTCHA widget here -->
            <input type="submit" value="Verify">
        </form>
    ''')

# Route to handle CAPTCHA verification
@app.route('/verify', methods=['POST'])
def verify():
    # Here you would verify the CAPTCHA response
    return 'Verification successful! You are now allowed to access the site.'

# Main route
@app.route('/')
def home():
    return 'Welcome to the site! Your IP is being monitored for security purposes.'

if __name__ == '__main__':
    app.run(host='192.168.23.219')

