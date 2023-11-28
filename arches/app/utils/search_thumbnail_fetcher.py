import base64
import copy
import re
from typing import List, Tuple
from urllib.error import HTTPError
from requests.exceptions import ConnectionError
import requests
from urllib.parse import urlparse, urlunparse


class SearchThumbnailFetcher(object):
    def __init__(self, resource):
        self.resource = resource

    def get_thumbnail(self, retrieve=False):
        pass
