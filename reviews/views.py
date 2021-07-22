from django.db.models import Subquery, OuterRef, Q
from rest_framework.response import Response

from group.models import Contract, Company
from .models import ReviewImage, Review, Comment
from rest_framework import viewsets, status, pagination
from .serializer import ReviewImageSerializer, ReviewSerializer, CommentSerializer


# Create your views here.
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination.PageNumberPagination.page_size = 5
    ordering = ['-created_at']
    company = None

    def get_queryset(self):
        queryset = Review.objects.all().order_by('-created_at')

        # 같은 회사 멤버이거나, 공개설정된 리뷰만 조회 가능
        # is user joined company?
        user = self.request.user
        contract = Contract.objects.filter(user_id=user).first()
        if contract:
            company_id = contract.company_id
            self.company = Company.objects.get(pk=company_id)
        if self.company:
            member = Contract.objects.filter(user=OuterRef('user')).filter(company=company_id).values('user')
            queryset = queryset.filter(Q(public=True) | Q(user__in=member))\
                .annotate(my_name=Subquery(member.values('my_name')))

        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        store = request.query_params.get('store')

        if store:
            queryset = queryset.filter(store=store)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class ReviewImageViewSet(viewsets.ModelViewSet):
    queryset = ReviewImage.objects.all()
    serializer_class = ReviewImageSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

