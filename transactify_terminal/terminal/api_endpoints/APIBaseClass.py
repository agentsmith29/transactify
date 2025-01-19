from transactify_terminal.settings import CONFIG
import requests
import logging

class APIBaseClass():

    def __init__(self, api_url):
        self.api_url = api_url
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.{self.__class__.__name__}")  