from rest_framework.decorators import action, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ReviewImage, Comment, Like
from rest_framework import viewsets, status
from .serializer import ReviewImageSerializer, CommentSerializer, CommentListSerializer, \
    LikeInReviewListSerializer, LikeSerializer
from .constants import LikeStatus


class ReviewImageViewSet(viewsets.ModelViewSet):
    queryset = ReviewImage.objects.all()
    serializer_class = ReviewImageSerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        if request.FILES:
            request.data.image = request.FILES
        if request.data['review']:
            request.data.review = request.data['review']
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk, *args, **kwargs):
        if request.FILES:
            request.data.image = request.FILES
        if request.data['review']:
            request.data.review = request.data['review']
        instance = ReviewImage.objects.get(pk=pk)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentListSerializer

    def get_serializer_context(self):
        context = super(CommentViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        queryset = Comment.objects.filter(parent_comment=None).order_by('-created_at')
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = CommentSerializer(data={**data, 'user': request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None, *args, **kwargs):
        data = request.data
        comment = Comment.objects.get(pk=pk)
        serializer = CommentSerializer(comment, data={**data, 'user': request.user.id}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.filter(status=LikeStatus.ACTIVE.value)
    serializer_class = LikeInReviewListSerializer

    def get_serializer_context(self):
        context = super(LikeViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        queryset = Comment.objects.filter(parent_comment=None).order_by('-created_at')
        return queryset

    def list(self, request):
        queryset = self.queryset
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    @permission_classes((IsAuthenticated,))
    def active(self, request):
        data = request.data
        user = request.user
        print(user, data['review'])
        if 'review' not in data:
            return Response({'message': '필수 파라미터가 누락되었습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            like = Like.objects.get(user=user, review=data['review'])
            if getattr(like, 'status') is LikeStatus.ACTIVE.value:
                return Response({'message': '이미 좋아한 게시물 입니다.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = LikeSerializer(like, data={'status': LikeStatus.ACTIVE.value}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(**serializer.validated_data)
            return Response({**serializer.data, 'message': '좋아요 성공'})
        except Like.DoesNotExist:
            serializer = LikeSerializer(data={**data, 'user': request.user.id})
            serializer.is_valid(raise_exception=True)
            Like.objects.create(**serializer.validated_data)
            return Response({**serializer.data, 'message': '좋아요 생성'})

    @action(detail=False, methods=['post'])
    @permission_classes((IsAuthenticated,))
    def inactive(self, request):
        data = request.data
        user = request.user
        if 'review' not in data:
            return Response({'message': '필수 파라미터가 누락되었습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            like = Like.objects.get(user=user, review=data['review'])
            if getattr(like, 'status') is LikeStatus.INACTIVE.value:
                return Response({'message': '이미 좋아요 취소한 게시물 입니다.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = LikeSerializer(like, data={'status': LikeStatus.INACTIVE.value}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(**serializer.validated_data)
            return Response({**serializer.data, 'message': '좋아요 취소'})
        except Like.DoesNotExist:
            return Response({'message': '존재하지 않습니다'}, status=status.HTTP_400_BAD_REQUEST)

