from rest_framework import pagination
from rest_framework.response import Response


class Pagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_page(),
            'previous': self.get_previous_page(),
            'results': data
        })

    def get_next_page(self):
        if not self.page.has_next():
            return None
        page_number = self.page.next_page_number()
        return page_number

    def get_previous_page(self):
        if not self.page.has_previous():
            return None
        page_number = self.page.previous_page_number()
        return page_number
