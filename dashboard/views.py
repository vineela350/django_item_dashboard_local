from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Category, Tag, Item
from .serializers import CategorySerializer, TagSerializer, ItemSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
#from rest_framework.decorators import api_view
from .serializers import UserSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.views.generic.list import ListView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from .serializers import PasswordResetSerializer
from django.contrib.auth.models import User
from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from .models import CustomUser


@swagger_auto_schema(method='post', request_body=ItemSerializer)
@swagger_auto_schema(
    method='get',
    responses={200: ItemSerializer(many=True)},
    manual_parameters=[
        openapi.Parameter('search', in_=openapi.IN_QUERY, description="Search items by name", type=openapi.TYPE_STRING),
        openapi.Parameter('category', in_=openapi.IN_QUERY, description="Filter by category ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('ordering', in_=openapi.IN_QUERY, description="Order items by a given field", type=openapi.TYPE_STRING),
    ]
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def item_list(request):
    if request.method == 'GET':
        # Filter and sort logic can be added here using request.query_params
        search_query = request.query_params.get('search', None)
        category_query = request.query_params.get('category', None)
        ordering = request.query_params.get('ordering', None)

        items = Item.objects.all()

        if search_query:
            items = items.filter(name__iexact=search_query)
        if category_query:
            items = items.filter(category__id=category_query)
        if ordering:
            items = items.order_by(ordering)

        serializer = ItemSerializer(items, many=True)
        return Response({'items': serializer.data})

    elif request.method == 'POST':
        serializer = ItemSerializer(data=request.data)
        #breakpoint()
        if serializer.is_valid():
            #breakpoint()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@swagger_auto_schema(
    method='get', 
    responses={200: ItemSerializer()}
)
@swagger_auto_schema(
    method='delete', 
    request_body=ItemSerializer,
    responses={204: 'Item deleted'}
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'GET':
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = ItemSerializer(item, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
@swagger_auto_schema(method='post', request_body=CategorySerializer)
@swagger_auto_schema(
    method='get',
    responses={200: CategorySerializer(many=True)},
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Search term", type=openapi.TYPE_STRING),
        # Add other parameters here
    ]
)   
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def category_list(request):
    if request.method == 'GET':

        categories = Category.objects.all()

        # Example filtering by a name field, adjust or remove if not applicable
        search_query = request.query_params.get('search', None)
        if search_query:
            categories = categories.filter(name__icontains=search_query)

        # Example sorting, adjust or remove if not applicable
        ordering = request.query_params.get('ordering', None)
        if ordering:
            categories = categories.order_by(ordering)

        serializer = CategorySerializer(categories, many=True)
        return Response({'categories': serializer.data})

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    return Response({'detail': 'A category with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@swagger_auto_schema(method='delete', request_body=CategorySerializer)
@swagger_auto_schema(method='get')    
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = CategorySerializer(category, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(method='post', request_body=TagSerializer)
@swagger_auto_schema(method='get')
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tag_list(request):
    if request.method == 'GET':
        # Retrieve all tags or filter them based on a provided search query
        tags = Tag.objects.all()
        search_query = request.query_params.get('search', None)
        if search_query:
            tags = tags.filter(name__icontains=search_query)

        serializer = TagSerializer(tags, many=True)
        return Response({'tags': serializer.data})

    elif request.method == 'POST':
        # Create a new tag instance from the provided data
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def tag_detail(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == 'GET':
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = TagSerializer(tag, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Create a token for the new user
            token, created = Token.objects.get_or_create(user=user)
            print("hii")
            #breakpoint()
            data = serializer.data
            data['token'] = token.key
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = None
        if '@' in username:
            try:
                user = User.objects.get(email=username)
            except ObjectDoesNotExist:
                pass

        if not user:
            user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ItemSearchListView(ListView):
    model = Item
    template_name = 'items/item_list.html'  # Specify your template name

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Item.objects.filter(name__icontains=query)
        return Item.objects.all()
    
@api_view(['POST'])
def forgot_password(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.get(email=serializer.validated_data['email'])
        serializer.update_password(user, serializer.validated_data['new_password'])
        return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)