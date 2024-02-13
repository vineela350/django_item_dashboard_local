"""
URL configuration for dashboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from dashboard import views
from django.contrib.auth import views as auth_views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view




schema_view = get_schema_view(
    openapi. Info(
        title="API",
        default_version='1.0.0',
        description="API documentation of App",
    ),
    public=True,
)


urlpatterns = [
    # path('api/v1/', include([
    # path("admin/", admin.site.urls),
    # path('api/categories/', views.category_list, name='category-list'),
    # path('api/categories/<int:pk>/', views.category_detail, name='category-detail'),
    # path('api/tags/', views.tag_list, name='tag-list'),
    # path('api/tags/<int:pk>/', views.tag_detail, name='tag-detail'),
    # path('api/items/', views.item_list, name='item-list'),
    # path('api/items/<int:pk>/', views.item_detail, name='item-detail'),
    # path('register/', views.register_user, name='register'),
    # path('login/', views.user_login, name='login'),
    # path('logout/', views.user_logout, name='logout'),
    # path('password_reset/', views.forgot_password, name='password_reset'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('swagger/schema/', schema_view.with_ui('swagger', cache_timeout=0), name="swagger-schema"),
    #      ])
    #      ),
    
    path('admin/', admin.site.urls),
    path('api/', include([
        path('categories/', views.category_list, name='category-list'),
        path('categories/<int:pk>/', views.category_detail, name='category-detail'),
        path('tags/', views.tag_list, name='tag-list'),
        path('tags/<int:pk>/', views.tag_detail, name='tag-detail'),
        path('items/', views.item_list, name='item-list'),
        path('items/<int:pk>/', views.item_detail, name='item-detail'),
        # ... other paths specific to the API ...
    ])),
    path('register/', views.register_user, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password_reset/', views.forgot_password, name='password_reset'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('swagger/schema/', schema_view.with_ui('swagger', cache_timeout=0), name="swagger-schema"),



]
