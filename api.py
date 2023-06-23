from flask.views import MethodView
from flask import Flask, jsonify, request, send_file, make_response, url_for
from models import User, db, Event, Order, Review
from werkzeug.security import generate_password_hash, check_password_hash
from flask import g, current_app
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
import os
import shutil 

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

class HomeApi(MethodView):
    def get(self):
        events = Event.query.order_by(Event.start_time).limit(4).all()

        response = []
        for event in events:
            event_data = {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'price': event.ticket_price,
                'image_url': event.image,
                'rating': event.rating
            }
            response.append(event_data)
        return response
class SearchApi(MethodView):
    def get(self):
        search_term = request.args.get('q').lower()
        events = Event.query.filter(Event.description.contains(search_term)
                                    | Event.title.contains(search_term)
                                    | Event.genra.contains(search_term)
                                    | Event.location.contains(search_term)
                                    | Event.address.contains(search_term)).all()
        response = []
        for event in events:
            event_data = {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'price': event.ticket_price,
                'image_url': event.image,
                'rating': event.rating
            }
            response.append(event_data)
        if not response:
            return jsonify({'message': 'No results found'}), 404
        else:
            return response
# Define a path for event images
EVENT_IMG_PATH = "eventImg/"

class EventApi(MethodView):
    # Create a new event
    def post(self, operation):
        if operation == 'create':
            title = request.form.get('title')
            description = request.form.get('description')
            genra = request.form.get('genra')
            location = request.form.get('location')
            address = request.form.get('address')
            start_time_str = request.form.get('start_time')
            end_time_str = request.form.get('end_time')
            hostname = request.form.get('hostname')
            
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
            # Check if the host exists
            host = User.query.filter_by(username=hostname).first()
            if host is None:
                return jsonify({'message': 'Host not found'}), 404

            event = Event(title=title, 
                            description=description, 
                            genra=genra, location=location, 
                            address=address, start_time=start_time, 
                            end_time=end_time, host_id=host.id)

            db.session.add(event)
            try:
                db.session.commit()
            except SQLAlchemyError as e:
                print(e)
                return jsonify({'message': 'Database error occurred'}), 500

            # Create a folder for this event's images
            os.makedirs(EVENT_IMG_PATH + str(event.id), exist_ok=True)

            # Check if the post request has the file part
            if 'image' not in request.files:
                return jsonify({'message': 'No file part in the request'}), 400

            file = request.files['image']
            # If the user does not select a file, the browser might
            # submit an empty file without a filename.
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400

            if file:  # If there is a file
                filename = secure_filename(file.filename)
                # Save it in the respective event's folder
                file.save(os.path.join(EVENT_IMG_PATH + str(event.id), filename))

            return jsonify({'message': 'Event created successfully'}), 201

    # Upload an image for an event
    def put(self, operation, event_id):
        if operation == 'update':
            event = Event.query.get(event_id)
            if event is None:
                return jsonify({'message': 'Event not found'}), 404

            # Check if the post request has the file part
            if 'file' not in request.files:
                return jsonify({'message': 'No file part in the request'}), 400

            file = request.files['file']
            # If the user does not select a file, the browser might
            # submit an empty file without a filename.
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400

            if file:  # If file exist
                filename = secure_filename(file.filename)
                # Save it in the respective event's folder
                file.save(os.path.join(EVENT_IMG_PATH + str(event_id), filename))

            return jsonify({'message': 'Image uploaded successfully'}), 200

    # Retrieve event details
    def get(self, operation):
        if operation == 'all':
            pass
        elif operation == 'get':
            event_id = request.args.get('id')
            event = Event.query.get(event_id)
            print(f"Event: {event}")
            if event is None:
                return jsonify({'message': 'Event not found'}), 404

            response = {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'genra': event.genra,
                'location': event.location,
                'address': event.address,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'host_id': event.host_id
            }
            return jsonify(response), 200
        elif operation == 'search':
            search_term = request.args.get('q').lower()
            events = Event.query.filter(Event.description.contains(search_term)
                                        | Event.title.contains(search_term)
                                        | Event.genra.contains(search_term)
                                        | Event.location.contains(search_term)
                                        | Event.address.contains(search_term)).all()
            response = []
            for event in events:
                event_data = {
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'price': event.ticket_price,
                    'image_url': event.image,
                    'rating': event.rating
                }
                response.append(event_data)
            if not response:
                return jsonify({'message': 'No results found'}), 404
            else:
                return response
    # Delete an event
    def delete(self, operation, event_id):
        if operation == 'delete':
            event = Event.query.get(event_id)
            if event is None:
                return jsonify({'message': 'Event not found'}), 404

            db.session.delete(event)
            try:
                db.session.commit()
            except SQLAlchemyError:
                return jsonify({'message': 'Database error occurred'}), 500

            # Delete the event's images
            shutil.rmtree(EVENT_IMG_PATH + str(event_id))

            return jsonify({'message': 'Event deleted successfully'}), 200

    # Get an image of an event
    def get_image(self, event_id, image_name):
        print("called get image")
        image_dir = os.path.join('eventImg', str(event_id))
        image_urls = []
        if image_name == None:
            for image in os.listdir(image_dir):
                print(image)
                image_path = os.path.join(image_dir, image)
                if os.path.isfile(image_path):
                    image_urls.append(image_path)
            return jsonify(image_urls)
        else:
            print(image_name)
            image_path = os.path.join(image_dir, image_name)
            if os.path.exists(image_path):
                image_urls.append(image_path)
                return jsonify(image_urls)
            else:
                print(f"not found {image_path}")
                return jsonify({'message': 'Image not found'}), 404