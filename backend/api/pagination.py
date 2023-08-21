from core import constants
from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """ Пагинация. """
    page_size = constants.DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
