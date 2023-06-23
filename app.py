# Import necessary modules
from flask import Flask, jsonify, request
#from flask_restful import Resource, Api #add flask restful
from extension import db, cors
from models import User
from api import AuthApi, HomeApi, SearchApi, EventApi
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
cors.init_app(app)

@app.route('/')
def hello_world():
    return "Hello World!"

@app.cli.command()
def create():
    db.drop_all()
    db.create_all()
    User.init_db()

# Register API rule
def register_api(view, endpoint, url, pk='operation', pk_type='string'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    app.add_url_rule(f'{url}/<string:{pk}>/', 
                        view_func=view_func, 
                        methods=['GET', 'POST', 'PUT', 'DELETE'])
    
register_api(AuthApi, 'auth_api', '/auth/', pk='operation', pk_type='string')
register_api(HomeApi, 'home_api', '/homePage/', pk='operation', pk_type='string')
register_api(EventApi, 'event_api', '/event/', pk='operation', pk_type='string')

@app.route('/event/<int:event_id>/image/', methods=['GET'])
def get_event_image(event_id):
    image_name = request.args.get('image_name') #for single image search
    print(image_name)
    return EventApi().get_image(event_id, image_name)

if __name__ == '__main__':
    app.run(debug=True)