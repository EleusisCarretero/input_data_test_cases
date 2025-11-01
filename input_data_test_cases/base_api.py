from abc import ABC, abstractmethod
from flask import Flask,jsonify
from enum import Enum


class StatusCode(int, Enum):
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    NOT_FOUND = 404



class BaseApiException(Exception):
    pass

class BaseApi(ABC):
      
    def __init__(self, config):
        self.app = Flask(__name__)
        self.config = config
        self.client = self.setup_client()
        self.define_routes()
    
    @abstractmethod
    def setup_client(self):
        raise BaseApiException("Rout are not defined")

    @abstractmethod
    def connect_data_base(self, **kwargs):
        raise BaseApiException("Rout are not defined")
    
    @abstractmethod
    def define_routes(self):
        raise BaseApiException("Rout are not defined")

    def run(self, debug):
        self.app.run(debug=debug)
    
    def format_response(self, response, status_code):
        return jsonify(response), status_code