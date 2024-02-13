from rest_framework import serializers
from .models import Category, Tag, Item
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        extra_kwargs = {'name': {'validators': []}} 

    

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = Item
        fields = ['id', 'sku', 'name', 'category', 'tags', 'in_stock', 'available_stock']
        depth = 1  # This will allow nested serialization

    def create(self, validated_data):
        # Handle the nested category object
        category_data = validated_data.pop('category')
        category = Category.objects.get(name=category_data['name'])
        
        # Handle nested tags objects
        tag_data_list = validated_data.pop('tags')
        item = Item.objects.create(category=category, **validated_data)
        
        # Create or get tags and add them to the item
        for tag_data in tag_data_list:
            tag, created = Tag.objects.get_or_create(**tag_data)
            item.tags.add(tag)
        
        return item

    def update(self, instance, validated_data):
        # Handle the nested category object
        category_data = validated_data.pop('category')
        category, created = Category.objects.get_or_create(**category_data)
        instance.category = category

        # Handle the rest of the fields
        instance.sku = validated_data.get('sku', instance.sku)
        instance.name = validated_data.get('name', instance.name)
        # ... handle other fields similarly

        instance.save()
        return instance
    
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['username', 'email', 'password']
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         user = CustomUser(
#             username=validated_data['username'],
#             email=validated_data['email']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user
    
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Password fields didn't match."})

        return attrs

    def update_password(self, user, new_password):
        user.set_password(new_password)
        user.save()


