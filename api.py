from flask.views import MethodView
from flask import Flask, jsonify, request
from models import User
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash
from extension import db

#create api class
class AuthApi(MethodView):
    #handle post request
    def post(self, operation):
        if operation == 'register':
            username = request.json.get('username')
            password = request.json.get('password')
            email = request.json.get('email')
            if not username or not password or not email:
                return jsonify({'message': 'All fields are required'}), 400
            user = User.query.filter_by(username=username).first()
            if user:
                return jsonify({'message': 'Username already exists'}), 400
            user = User(username=username, email=email)
            user.password_hash = generate_password_hash(password)
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

            return jsonify({'message': 'Logged in successfully'}), 200
    
    #handle get request
    def get(self, operation, user_id=None):
        if operation == 'view':
            if user_id is None:
                users: List[User] = User.query.all()
                result = [
                    {
                        'id': user.id,
                        'username': user.username,
                        'password': user.password,
                        'email': user.email,
                    } for user in users
                ]
                return jsonify({
                    'status': 'success',
                    'message': 'request successful',
                    'results': result
                })
            else:
                user: User = User.query.get(user_id)
                if user is None:
                    return jsonify({
                        'status': 'error',
                        'message': 'User not found',
                    }), 404

                return jsonify({
                    'status': 'success',
                    'message': 'request successful',
                    'results': {
                        'id': user.id,
                        'username': user.username,
                        'password': user.password,
                        'email': user.email
                    }
                })
    
    