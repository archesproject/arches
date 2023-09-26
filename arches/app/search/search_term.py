from django.utils.translation import get_language


class SearchTerm(object):
    def __init__(self, value=None, lang=None):
        self.value = value
        self.lang = lang if lang is not None else get_language()
