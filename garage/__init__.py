import re
import werkzeug as tool
import redis
from flask import (Flask, request, Response, jsonify, abort)
from collections import OrderedDict

# addressRegex = ""
# garageRegex = "^g[0-9]" # Do we need it?
licenseRegex = "^[A-Z0-9]{1,7}$"

def create_app():
    app = Flask(__name__)
    redisClient = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def garageKey(garageNo):
        return f'Garage:{garageNo}'
    
    def spotKey(garageNo, spotNo):
        return f'Spot:{garageNo}:{spotNo}'

    # Išvalyti duomenų bazę
    @app.route('/flushall', methods=['POST'])
    def flush ():
        redisClient.flushall()
        return "", 200

    # Užregistruoti garažą.
    @app.route('/garage', methods=['PUT'])
    def set_garage():
        reqBody = request.json
        id = reqBody.get("id")
        spots = reqBody.get("spots")
        address = reqBody.get("address")

        if (id != None and spots != None and address != None):
            if (spots > 0):
                garage = redisClient.get(garageKey(id))
                if (garage == None):
                    garageValue = f"{id}:{spots}:{address}"
                    redisClient.set(garageKey(id), garageValue)
                    return '', 201
                else:
                    return {"message": "Garage with the following ID is already registered"}, 400
            else: 
                return {"message": "Number of spots should be higher than 0"}, 400 
        else:
           return {"message": "Id, spots or address is missing"}, 400
        
    # Gauti garažo informaciją.
    @app.route('/garage/<garageId>', methods=['GET'])
    def get_garage(garageId):
        garage = redisClient.get(garageKey(garageId))
        if (garage != None):
            garageInfo = garage.split(':')
            
            response = (
                f'{{"id": "{garageInfo[0]}",'
                f'"spots": {int(garageInfo[1])},'
                f'"address": "{garageInfo[2]}"}}'
            )
            return Response(response, mimetype='application/json'), 200

            # return {
            #     "id": garageInfo[0],
            #     "spots": int(garageInfo[1]),
            #     "address": garageInfo[2],
            # }
        else: 
            return {"message": "Garage not found"}, 404
    
    # Gauti bendrą vietų skaičių garaže.
    @app.route('/garage/<garageId>/configuration/spots', methods=['GET'])
    def get_spots(garageId):
        garage = redisClient.get(garageKey(garageId))
        if (garage != None):
            garageInfo = garage.split(':')

            return {
                "spots": int(garageInfo[1])
            }, 200
        else: 
            return {"message": "Garage not found"}, 404
    
    # Pakeisti garažo vietų skaičių.
    @app.route('/garage/<garageId>/configuration/spots', methods=['POST'])
    def update_garage_spots(garageId):
        reqBody = request.json
        spots = int(reqBody.get("spots"))
        if (spots != None):
            if (spots > 0):
                garage = redisClient.get(garageKey(garageId))
                if (garage != None):
                    garageInfo = garage.split(':')
                    old_spots = int(garageInfo[1])
                    if (spots >= old_spots):
                        garageValue = f"{garageInfo[0]}:{spots}:{garageInfo[2]}"
                        redisClient.set(garageKey(garageId), garageValue)
                        return "", 200
                    else:
                        for spotNo in range(spots, old_spots + 1):
                            license = redisClient.get(spotKey(garageId, spotNo))
                            if (license != None):
                                return {"message": f'spot {spotNo} is not empty'}, 400
                        return "", 200
                else:
                    return {"message": "Garage not found"}, 404
            else:
                return {"message": "Number of spots should be higher than 0"}, 400
        else:
            return {"message": "Invalid request body"}, 400
        
        # padidinti visad galiu
        # jei noriu sumažinti:
            # pasiimu tą range nuo to, iki kurio 
            # jei randu bent vieną užimtą spot'ą, sakau, kad ta vieta yra užimta

    # Užregistruoti užimtą vietą garaže.
    @app.route('/garage/<garageId>/spots/<spotNo>', methods=['POST'])
    def update_spot(garageId, spotNo):
        garage = redisClient.get(garageKey(garageId))
        if (garage != None):
            garageInfo = garage.split(':') 
            spots = int(garageInfo[1])
            if (int(spotNo) <= spots and int(spotNo) > 0):
                str, num = get_spot_license(garageId, spotNo)
                if (num == 204):
                    reqBody = request.json
                    license = reqBody.get("licenseNo")
                    redisClient.set(spotKey(garageInfo[0], spotNo), license)
                    return ''
                else:
                    return {"message": "Spot is already taken"}, 400
            else:
                return {"message": "Spot number not found"}, 404
        else: 
            return {"message": "Garage not found"}, 404
    
    # Gauti automoblio numerį, kuris užima vietą.
    @app.route('/garage/<garageId>/spots/<spotNo>', methods=['GET'])
    def get_spot_license(garageId, spotNo):
        garage = redisClient.get(garageKey(garageId))
        if (garage != None):
            garageInfo = garage.split(':') 
            spots = int(garageInfo[1])
            if int(spotNo) <= spots and int(spotNo) > 0:
                license = redisClient.get(spotKey(garageId, spotNo))
                if (license != None):
                    return license, 200
                else:
                    return {"message": "Spot is free"}, 204
            else:
                return {"message": "Spot number not found"}, 404
        else: 
            return {"message": "Garage not found"}, 404

    # Pažymėti vietą laisva.
    @app.route('/garage/<garageId>/spots/<spotNo>', methods=['DELETE'])
    def delete_spot_license(garageId, spotNo):
        garage = redisClient.get(garageKey(garageId))
        if (garage != None):
            garageInfo = garage.split(':') 
            spots = int(garageInfo[1])
            if int(spotNo) <= spots and int(spotNo) > 0:
                redisClient.delete(spotKey(garageId, spotNo))
                return '', 200
            else:
                return {"message": "Spot number not found"}, 404
        else: 
            return {"message": "Garage not found"}, 404
    
    # Gauti laisvų ir užimtų vietų skaičių garaže.
    @app.route('/garage/<garageId>/status', methods=['GET'])
    def get_garage_status(garageId):
        garage = redisClient.get(garageKey(garageId))
        if (garage != None):
            garageInfo = garage.split(':') 
            spots = int(garageInfo[1])

            _, keys = redisClient.scan(match=spotKey(garageId, '*'))
            occupiedSpots = len(keys)
            freeSpots = spots - occupiedSpots

            return {
                "freeSpots": freeSpots,
                "occupiedSpots": occupiedSpots
            }   
        else: 
            return {"message": "Garage not found"}, 404

    return app