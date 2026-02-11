from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import BookViewSet, book_stats, search_books

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', book_stats, name='book-stats'),
    path('search/', search_books, name='book-search'),
]