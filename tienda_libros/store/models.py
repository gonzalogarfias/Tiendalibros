from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    ebook_file = models.FileField(upload_to='ebooks/', null=True, blank=True)
    is_virtual = models.BooleanField(default=True)  
    stock = models.IntegerField(default=0) # Añadido para el stock de libros físicos

    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title