from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from matzip.handler import request_data_handler
from stores.models import Keyword
from stores.serializers.keword import KeywordSerializer, KeywordCreateSerializer


class KeywordViewSet(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('-created_at')
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        keyword = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(keyword)
        return Response({**serializer.data, 'message': '키워드를 조회했습니다.'}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request_data_handler(request.data, ['name', 'team'], ['category'])
        keyword = self.queryset.filter(naem=data['name'], team=data['team']).first()
        if keyword:
            keyword.hit_count += 1
            keyword.save()
            serializer = self.serializer_class(keyword)
            return Response({**serializer.data, 'message': '키워드를 업데이트 했습니다.'})
        else:
            serializer = KeywordCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = self.serializer_class(serializer.instance)
            return Response({**serializer.data, 'message': '키워드를 생성했습니다.'})
        # keyword object create or update 생성 필요
