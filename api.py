from flask.views import MethodView
from flask import Flask, jsonify, request
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import g, current_app
from datetime import datetime, timedelta

class AuthApi(MethodView):
    # handle post request
    def post(self, operation):
        if operation == 'register':
            username = request.json.get('username')
            password = request.json.get('password')
            email = request.json.get('email')
            payment_info = request.json.get('payment_info')
            is_host = request.json.get('is_host', '').lower() == 'true'

            if not username or not password or not email or not payment_info:
                return jsonify({'message': 'All fields are required'}), 400

            user = User.query.filter_by(username=username).first()
            if user:
                return jsonify({'message': 'Username already exists'}), 400
            email = User.query.filter_by(email=email).first()
            if email:
                return jsonify({'message': 'Email already exists'}), 400
            user = User(username=username, email=email, payment_info=payment_info, is_host=is_host)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            return jsonify({'message': 'User created successfully'}), 201

        elif operation == 'login':
            username = request.json.get('username')
            password = request.json.get('password')

            if not username or not password:
                return jsonify({'message': 'Both fields are required'}), 400

            user = User.query.filter_by(username=username).first()

            if not user or not user.check_password(password):
                return jsonify({'message': 'Invalid credentials'}), 401

            return jsonify({'token': 'login sunccess'}),200
