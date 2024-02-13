from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Item, Category, Tag
from .serializers import ItemSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ItemListAPITest(APITestCase):
    def setUp(self):
        # Create a category
        self.category = Category.objects.create(name='Test Category')

        # Create some tags
        self.tag1 = Tag.objects.create(name='Tag 1')
        self.tag2 = Tag.objects.create(name='Tag 2')

        # Create items
        self.item1 = Item.objects.create(sku='SKU1', name='Item 1', category=self.category, in_stock=True, available_stock=10)
        self.item1.tags.add(self.tag1)

        self.item2 = Item.objects.create(sku='SKU2', name='Item 2', category=self.category, in_stock=False, available_stock=5)
        self.item2.tags.add(self.tag2)

        self.url = reverse('item-detail', kwargs={'pk': self.item1.pk})

    def test_get_items(self):
        url = reverse('item-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure both items are returned
        self.assertEqual(len(response.data['items']), 2)

        # Ensure the response contains the correct data
        item1_data = {
            'id': self.item1.id,
            'sku': 'SKU1',
            'name': 'Item 1',
            'category': {
                'id': self.category.id,
                'name': 'Test Category'
            },
            'tags': [{
                'id': self.tag1.id,
                'name': 'Tag 1'
            }],
            'in_stock': True,
            'available_stock': '10.00'
        }
        self.assertIn(item1_data, response.data['items'])
        

    def test_filter_items_by_search_query(self):
        url = reverse('item-list')
        response = self.client.get(url + '?search=Item 1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['name'], 'Item 1')

    def test_filter_items_by_category(self):
        url = reverse('item-list')
        response = self.client.get(url + f'?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 2)

    def test_order_items_by_name(self):
        url = reverse('item-list')
        response = self.client.get(url + '?ordering=name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 2)
        self.assertEqual(response.data['items'][0]['name'], 'Item 1')

    def test_create_item(self):
    # Define the URL for the item creation endpoint
    # Replace 'item-create' with the actual name of your item creation endpoint
        url = reverse('item-list')
        
        # Prepare the data for creating a new item
        # Ensure 'sku' is unique and 'category' is set to the ID of an existing Category instance
        data = {
            'sku': 'SKU_UNIQUE',  # Make sure this is unique to avoid conflicts with existing items
            'name': 'New Test Item',
            "category": {
                "id": self.category.id,
                "name": self.category.name
            },
             'tags': [
                {
                    "id": self.tag1.id,
                    "name": self.tag1.name
                },
                {
                    "id": self.tag2.id,
                    "name": self.tag2.name
                }
            ],
              # Assuming you want to associate both tags created in setUp
            'in_stock': True,
            'available_stock': '15.00',  # Ensure this is a string formatted as a decimal
        }

        # Make the POST request to create a new item
        response = self.client.post(url, data, format='json')

        # Check if the response status code is 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_item(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.item1.name) 

    def test_delete_item(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

            # Ensure the item is deleted from the database
        with self.assertRaises(Item.DoesNotExist):
            Item.objects.get(pk=self.item1.pk)

    def test_create_category_success(self):
        url = reverse('category-list')  # Replace 'category-list' with your actual URL name for category_list view
        data = {'name': 'New Category'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.get().name, 'New Category')
    
    def test_create_category_duplicate_name(self):
        # Create an initial category to cause a duplicate error on the second post
        Category.objects.create(name='Existing Category')

        url = reverse('category-list')  # Ensure this matches your actual URL name
        duplicate_data = {'name': 'Existing Category'}
        response = self.client.post(url, duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'A category with this name already exists.')
        self.assertEqual(Category.objects.count(), 1)  # Ensure no new category was added


    

