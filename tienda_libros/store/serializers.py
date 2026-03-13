from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    # Esto permite que el JS lea "uploaded_by_username" como espera tu template
    uploaded_by_username = serializers.ReadOnlyField(source='uploaded_by.username')
    # Asegura que la URL de la imagen sea completa
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'price', 'description', 
            'cover_image_url', 'is_virtual', 'stock', 'uploaded_by_username'
        ]

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        return None