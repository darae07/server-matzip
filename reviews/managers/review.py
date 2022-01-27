from django.db import models
from django.db.models.manager import BaseManager


class ReviewQuerySet(models.QuerySet):
    pass


class ReviewManger(BaseManager.from_queryset(ReviewQuerySet)):
    def create(self, keyword, content, team_member):
        if not keyword:
            raise ValueError('필수 파라미터 keyword 가 누락되었습니다.')
        if not content:
            raise ValueError('필수 파라미터 content 가 누락되었습니다.')
        if not team_member:
            raise ValueError('필수 파라미터 team_member 가 누락되었습니다.')
        review = self.model(keyword_id=keyword, content=content, team_member_id=team_member)
        review.save()
        return review


class ReviewImageQuerySet(models.QuerySet):
    pass


class ReviewImageManager(BaseManager.from_queryset(ReviewImageQuerySet)):
    def create(self, review, image):
        if not review:
            raise ValueError('필수 파라미터 review 가 누락되었습니다.')
        if not image:
            raise ValueError('필수 파라미터 image 가 누락되었습니다.')
        review_image = self.model(review_id=review, image=image)
        review_image.save()
        return review_image

