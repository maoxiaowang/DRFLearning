from rest_framework.pagination import PageNumberPagination as _PageNumberPagination


class PageNumberPagination(_PageNumberPagination):
    page_size_query_param = 'page_size'


class UnlimitedPagination(PageNumberPagination):

    def get_page_size(self, request):
        return 999999
