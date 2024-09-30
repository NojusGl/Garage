import re
import werkzeug as tool
import redis
from flask import (Flask, request, jsonify, abort)
# this is my comment

#TODO specify address regex
addressRegex = ""
garageRegex = "^g[0-9]" #NOTE Do we need it? Probably
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
        reqBody = request.json
        id = reqBody.get("id")
        spots = reqBody.get("spots")
        address = reqBody.get("address")

        if id != None and spots != None and address != None:
            if spots > 0:
                garageValue = f"{id}:{spots}:{address}"
                redisClient.set(garageKey(id), garageValue)
                return '', 201
            else: 
                return {"message": "Number of spots should be higher than 0"}, 400 
        else:
           return {"message": "Id, spots or address is missing"}, 400
        
    #Gauti garažo informaciją.
    @app.route('/garage/<garageId>', methods=['GET'])
    def get_garage():
        pass
    
    #Gauti bendrą vietų skaičių garaže.
    @app.route('/garage/<garageId>/configuration/spots', methods=['GET'])
    def get_spots(garageId):
        if re.search(garageRegex, garageId) != None:
            garage = redisClient.get(garageKey(garageId))
            if (garage != None):
                garageInfo = garage.split(':')

                return {
                    "spots": int(garageInfo[1])
                }
            else: 
                return {"message": "Garage not found"}, 404
        return {"message": "Invalid garageId"}, 400
    
    #Pakeisti garažo vietų skaičių.
    @app.route('/garage/<garageId>/configuration/spots', methods=['POST'])
    def update_garage_spots():
        pass

    #Užregistruoti užimtą vietą garaže.
    @app.route('/garage/<garageId>/spots/<spotNo>', methods=['POST'])
    def update_spot(garageId, spotNo):
        if re.search(garageRegex, garageId) != None:
            garage = redisClient.get(garageKey(garageId))
            if (garage != None):
                garageInfo = garage.split(':') 
                spots = int(garageInfo[1])
                if int(spotNo) <= spots and int(spotNo) > 0:
                    reqBody = request.json
                    license = reqBody.get("licenseNo")
                    redisClient.set(spotKey(spotNo), license)
                    return ''
                else:
                    return {"message": "Spot number not found"}, 404
            else: 
                return {"message": "Garage not found"}, 404
        return {"message": "Invalid garageId"}, 400
    
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
    def get_garage_status(garageId):
        if re.search(garageRegex, garageId) != None:
            garage = redisClient.get(garageKey(garageId))
            if (garage != None):
                garageInfo = garage.split(':') 
                spots = int(garageInfo[1])
                freeSpots = 0
                occupiedSpots = 0
                for spotNo in range(1, spots+1):
                    spot = redisClient.get(spotKey(spotNo))
                    if spot == None: freeSpots+=1
                    else: occupiedSpots+=1

                return {
                    "freeSpots": freeSpots,
                    "occupiedSpots": occupiedSpots
                }
            else: 
                return {"message": "Garage not found"}, 404
        return {"message": "Invalid garageId"}, 400

    return app