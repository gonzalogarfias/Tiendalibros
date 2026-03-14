from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import BookViewSet, search_books, book_stats

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', search_books, name='search_books'),
    path('stats/', book_stats, name='book_stats'),
]
