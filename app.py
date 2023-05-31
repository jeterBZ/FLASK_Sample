# Import necessary modules
from flask import Flask, jsonify, request
from extension import db, cors
from models import User
from api import AuthApi
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

    if endpoint == 'auth_api':
        # Add a rule for operations that don't require a user_id
        app.add_url_rule(f'{url}<string:{pk}>', 
                            view_func=view_func, 
                            methods=['GET'])
        # Add a rule for operations that do require a user_id
        app.add_url_rule(f'{url}<string:{pk}>/<int:user_id>', 
                            view_func=view_func, 
                            methods=['GET', 'PUT', 'DELETE'])
    
register_api(AuthApi, 'auth_api', '/auth/', pk='operation', pk_type='string')

if __name__ == '__main__':
    app.run(debug=True)