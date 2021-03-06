from django.db import IntegrityError
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Folder
from .serializers import LoginSerializer, UserSerializer, FolderSerializer, \
    FileSerializer


class UserRegistrationView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            status_code = status.HTTP_201_CREATED
            data = {
                'status code': status_code,
                'response': 'User created successfully',
                'username': serializer.data['username']
            }
            return Response(data, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            status_code = status.HTTP_200_OK
            data = {
                'status code': status_code,
                'response': 'User logged in successfully',
                'token': serializer.data['token'],
            }
            return Response(data, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})
        serializer = self.serializer_class(
            request.user,
            data=serializer_data,
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FolderView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def post(self, request):
        try:
            folder = Folder.objects.create(
                name=request.data.get('folder_name'),
                parent_id=request.data.get('folder'),
                owner=request.user
            )
            return Response(
                {
                    'folder': folder.id,
                    'folder_name': folder.name,
                    'folder_owner': folder.owner.id,
                }
            )
        except IntegrityError:
            return Response(
                {
                    'status': 'A folder with that name already exists',
                }
            )

    def get(self, request):
        try:
            folder = Folder.objects.get(
                pk=request.data.get('folder')
            )
            folder_serializer = FolderSerializer(
                folder.children.all(),
                many=True
            )
            file_serializer = FileSerializer(
                folder.files.all(),
                many=True
            )
            return Response(
                {
                    'folders': folder_serializer.data,
                    'files': file_serializer.data,
                }
            )
        except Folder.DoesNotExist:
            return Response(
                {
                    'response': 'Folder does not exist',
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request):
        try:
            folder = Folder.objects.get(
                pk=request.data.get('folder')
            )
            folder.delete()
            return Response(
                {
                    'response': f'Folder {folder.name} remove'
                },
                status=status.HTTP_200_OK
            )
        except Folder.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class FolderMoveView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def post(self, request):
        folder = Folder.objects.get(
            pk=request.data.get('from_folder')
        )
        folder.parent_id = request.data.get('to_folder')
        folder.save()
        return Response(
            {
                'ok': folder.path,
            }
        )
