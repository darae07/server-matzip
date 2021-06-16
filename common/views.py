from rest_framework import generics
from .serializers import ProfileSerializer
from .models import Profile

# Create your views here


class ProfileUpdateAPI(generics.UpdateAPIView):
    lookup_field = 'user_pk'
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
