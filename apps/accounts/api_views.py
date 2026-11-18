from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, UserProfile
from .serializers import UserSerializer, RegisterSerializer, UserProfileSerializer

class APIRegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APILoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class APILogoutView(views.APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})


class APIProfileView(views.APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            profile_data = request.data.get('profile')
            if profile_data:
                profile = getattr(request.user, 'profile', None)
                if profile:
                    p_ser = UserProfileSerializer(profile, data=profile_data, partial=True)
                    if p_ser.is_valid():
                        p_ser.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
