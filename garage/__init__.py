import re
import werkzeug as tool
import redis
from flask import (Flask, request, jsonify, abort)

#TODO specify address regex
addressRegex = ""
garageRegex = "" #NOTE Do we need it? Probably
licenseRegex = "^[A-Z0-9]{1,7}$"

def create_app():
    app = Flask(__name__)
    redisClient = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def garageKey(garageNo):
        return f'Garage:{garageNo}'
    
    def spotKey(spotNo):
        return f'Spot:{spotNo}'

    #Užregistruoti garažą.
    @app.route('/garage', methods=['PUT'])
    def set_garage():
        pass
    
    #Gauti garažo informaciją.
    @app.route('/garage/<garageId>', methods=['GET'])
    def get_garage():
        pass
    
    #Gauti bendrą vietų skaičių garaže.
    @app.route('/garage/<garageId>/configuration/spots', methods=['GET'])
    def get_spots():
        pass
    
    #Pakeisti garažo vietų skaičių.
    @app.route('/garage/<garageId>/configuration/spots', methods=['POST'])
    def update_garage_spots():
        pass

    #Užregistruoti užimtą vietą garaže.
    @app.route('/garage/<garageId>/spots/<spotNo>', methods=['POST'])
    def update_spot():
        pass
    
    #Gauti automoblio numerį, kuris užima vietą.
    @app.route('/garage/<garageId>/spots/<spotNo>', methods=['GET'])
    def get_spot_license():
        pass
    
    #Pažymėti vietą laisva.
    @app.route('/garage/<garageId>/spots/<spotNo>', methods=['DELETE'])
    def delete_spot_license():
        pass
    
    #Gauti laisvų ir užimtų vietų skaičių garaže.
    @app.route('/garage/<garageId>/status', methods=['GET'])
    def get_garage_status():
        pass

    return app