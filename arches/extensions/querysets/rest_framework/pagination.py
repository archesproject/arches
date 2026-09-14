from django.conf import settings
from rest_framework.pagination import LimitOffsetPagination


class ArchesLimitOffsetPagination(LimitOffsetPagination):
    default_limit = settings.API_MAX_PAGE_SIZE
