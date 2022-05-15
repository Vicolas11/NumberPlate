from rest_framework.views import APIView
from anpr_app.api.serializers import (ChangePasswordSerializer, ProfileUpdateSerializer, SigninSerializer, SignupSerializer)
from anpr_app.models import User
from rest_framework import status, authentication
from django.contrib import messages
from rest_framework.generics import CreateAPIView, UpdateAPIView, get_object_or_404
from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework.permissions import AllowAny
from django.utils.translation import gettext_lazy as _


class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):
    def enforce_csrf(self, request):        
        return


class RegisterView(CreateAPIView):
    serializer_class = SignupSerializer
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)   
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            messages.error(request, serializer.errors)      
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SigninView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SigninSerializer
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email__iexact=serializer.data['email'])
        login(request, user)
        response = {
            'success' : 'True',
            'status code' : status.HTTP_200_OK,
            'message': 'User logged in successfully',
            'user' : serializer.data['email']
        }
        status_code = status.HTTP_200_OK
        messages.success(request, 'Login Successfully')
        return Response(response, status=status_code)


class SignoutView(APIView):

    def post(self, request):
        logout(request)
        response = Response()
        response.data = {
            'status': status.HTTP_200_OK,
            'message': 'User Successfully Logout!'
        }
        return response


class ProfileUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileUpdateSerializer
    
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.request.user.pk)
        return obj

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'Message': 'Profile Updated Succesfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.request.user.pk)
        return obj

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'Message': 'Updated Succesfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
