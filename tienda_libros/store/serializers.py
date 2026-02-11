from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 
            'title', 
            'author', 
            'price', 
            'description', 
            'cover_image_url',
            'is_virtual', 
            'stock', 
            'uploaded_by_username',
            'uploaded_at'
        ]
    
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
        return None
