# Third-party modules
from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    '''Project-wide page-number pagination defaults.'''

    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50
