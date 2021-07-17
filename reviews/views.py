from django.db.models import Subquery, OuterRef
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

        # is user joined company?
        user = self.request.user
        contract = Contract.objects.filter(user_id=user).first()
        if contract:
            company_id = contract.company_id
            self.company = Company.objects.get(pk=company_id)
        if self.company:
            member = Contract.objects.filter(user=OuterRef('user')).filter(company=company_id).values('user')
            queryset = queryset.annotate(my_name=Subquery(member.values('my_name')))

        return queryset


class ReviewImageViewSet(viewsets.ModelViewSet):
    queryset = ReviewImage.objects.all()
    serializer_class = ReviewImageSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

