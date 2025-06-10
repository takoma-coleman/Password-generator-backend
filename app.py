# backend/app.py
import os
import random
import string
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_migrate import Migrate  # <-- new import

from db import db
from models import PasswordHistory
from auth import auth_bp

# Load .env into environment
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)  # <-- initialize Flask-Migrate here

jwt = JWTManager(app)

# Configure CORS with credentials support and specific origin
CORS(app, supports_credentials=True, origins=[
    'http://localhost:3000',
    'https://password-generator-frontend.onrender.com'
])


# Register auth blueprint
app.register_blueprint(auth_bp)

@app.route('/generate-password', methods=['POST'])
@jwt_required()
def generate_password():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    length = int(data.get('length', 12))
    include_numbers = bool(data.get('include_numbers', False))
    include_specials = bool(data.get('include_specials', False))
    count = int(data.get('count', 1))

    # Build character pool
    chars = string.ascii_letters
    if include_numbers:
        chars += string.digits
    if include_specials:
        chars += string.punctuation

    passwords = [''.join(random.choice(chars) for _ in range(length)) for _ in range(count)]

    # Save history
    entry = PasswordHistory(
        user_id=user_id,
        length=length,
        include_numbers=include_numbers,
        include_specials=include_specials,
        count=count,
        passwords='\n'.join(passwords)
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({'passwords': passwords}), 200

@app.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    entries = PasswordHistory.query.filter_by(user_id=user_id).order_by(PasswordHistory.timestamp.desc()).all()

    history_list = []
    for e in entries:
        history_list.append({
            'timestamp': e.timestamp.isoformat(),
            'length': e.length,
            'include_numbers': e.include_numbers,
            'include_specials': e.include_specials,
            'count': e.count,
            'passwords': e.passwords.split('\n')
        })

    return jsonify({'history': history_list}), 200

if __name__ == '__main__':
    # You can remove the db.create_all() call since we'll use migrations
    app.run(debug=True)
