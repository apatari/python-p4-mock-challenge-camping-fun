#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

api = Api(app)

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

class CamperIndex(Resource):

    def get(self):

        response_body = [camper.to_dict(only=('id', 'name', 'age')) for camper in Camper.query.all()]
        return response_body, 200
    
    def post(self):
        data = request.get_json()

        try:
            new_camper = Camper(name=data['name'], age=data['age'])
            db.session.add(new_camper)
            db.session.commit()

            return new_camper.to_dict(rules=('-signups',)), 201
        except Exception as err:
            return {"errors": ["validation errors"]}, 400
    
class CamperByID(Resource):

    def get(self, id):

        camper = Camper.query.filter_by(id=id).first()

        if camper:
            return camper.to_dict(), 200
        else:
            return {"error": "Camper not found"}, 404
        
        
    def patch(self, id):
        data = request.get_json()

        camper = Camper.query.filter_by(id=id).first()

        if not camper:
            return {"error": "Camper not found"}, 404
        else:
            try:
                camper.age = data['age']
                camper.name = data['name']
                db.session.commit()

                return camper.to_dict(only=('id', 'name', 'age')), 202
            
            except Exception as err:
                return {"errors": ["validation errors"]}, 400

class ActivitiesIndex(Resource):

    def get(self):
        activities = [activity.to_dict(rules=('-signups',)) for activity in Activity.query.all()]

        return activities, 200
    
class ActivitiesByID(Resource):

    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()

        if activity:
            db.session.delete(activity)
            db.session.commit()

            return {}, 204
        else:
            return {"error": "Activity not found"}, 404
        
class Signups(Resource):

    def post(self):
        data = request.get_json()

        try:
            new_signup = Signup(
                                camper_id=data['camper_id'], 
                                activity_id=data['activity_id'], 
                                time=data['time']
                                )
            db.session.add(new_signup)
            db.session.commit()

            return new_signup.to_dict(), 201
        except:
            return {"errors": ["validation errors"]}, 400

api.add_resource(Signups, '/signups')
api.add_resource(ActivitiesByID, '/activities/<int:id>')
api.add_resource(ActivitiesIndex, '/activities')
api.add_resource(CamperIndex, '/campers')
api.add_resource(CamperByID, '/campers/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
