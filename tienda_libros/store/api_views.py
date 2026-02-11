from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Book
from .serializers import BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de libros
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_queryset(self):
        queryset = Book.objects.all()
        tipo = self.request.query_params.get('tipo', None)
        
        if tipo == 'virtual':
            queryset = queryset.filter(is_virtual=True)
        elif tipo == 'fisico':
            queryset = queryset.filter(is_virtual=False)
        
        return queryset.order_by('-uploaded_at')
    
    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        """
        Endpoint para comprar un libro físico
        """
        book = self.get_object()
        
        if not book.is_virtual and book.stock > 0:
            book.stock -= 1
            book.save()
            serializer = self.get_serializer(book)
            return Response({
                'success': True,
                'message': 'Compra realizada exitosamente',
                'book': serializer.data
            })
        elif book.is_virtual:
            return Response({
                'success': False,
                'message': 'Este es un libro virtual, no requiere compra'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'message': 'Libro sin stock disponible'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def book_stats(request):
    """
    Endpoint para obtener estadísticas de libros
    """
    total_books = Book.objects.count()
    virtual_books = Book.objects.filter(is_virtual=True).count()
    physical_books = Book.objects.filter(is_virtual=False).count()
    
    return Response({
        'total': total_books,
        'virtual': virtual_books,
        'physical': physical_books
    })


@api_view(['GET'])
def search_books(request):
    """
    Endpoint para buscar libros por título o autor
    """
    query = request.query_params.get('q', '')
    
    if not query:
        return Response({
            'success': False,
            'message': 'Proporciona un término de búsqueda'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    books = Book.objects.filter(
        title__icontains=query
    ) | Book.objects.filter(
        author__icontains=query
    )
    
    serializer = BookSerializer(books, many=True, context={'request': request})
    
    return Response({
        'success': True,
        'count': books.count(),
        'results': serializer.data
    })