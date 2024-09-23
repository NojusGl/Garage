import re
import werkzeug as tool
import redis
from flask import (Flask, request, jsonify, abort)

regex = "^[A-Z0-9]{1,7}$"

def create_app():
    app = Flask(__name__)
    redisClient = redis.Redis(host='localhost', port=6379, decode_responses=True)

    return app