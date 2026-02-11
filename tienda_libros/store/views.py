from django.shortcuts import render, redirect, get_object_or_404
from django.http import StreamingHttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import Book
from .forms import BookUploadForm, ContactForm, PaymentForm

# Create your views here.

def home(request):
    tipo = request.GET.get('tipo')  
    
    if tipo == 'virtual':
        books = Book.objects.filter(is_virtual=True)
    elif tipo == 'fisico':
        books = Book.objects.filter(is_virtual=False)
    else:
        books = Book.objects.all()  
    
    return render(request, 'home.html', {
        'books': books,
        'tipo_actual': tipo  
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def upload_book(request):
    if request.method == 'POST':
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.uploaded_by = request.user
            book.save()
            return redirect('home')
    else:
        form = BookUploadForm()
    return render(request, 'upload_book.html', {'form': form})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            send_mail(
                'Contacto desde Librería',
                f'Nombre: {name}\nEmail: {email}\nMensaje: {message}',
                settings.EMAIL_HOST_USER,  
                ['tu_email@destino.com'],  
                fail_silently=False,
            )
            return render(request, 'contact.html', {'form': form, 'success': True})
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        if book.book_type == 'physical' and book.stock > 0:
            book.stock -= 1
            book.save()
        
        session_key = f"bought_{book.id}"
        request.session[session_key] = True
        
        return redirect('book_detail', book_id=book.id)
    
    already_bought = request.session.get(f"bought_{book.id}", False)
    
    return render(request, 'book_detail.html', {
        'book': book,
        'already_bought': already_bought
    })

def read_ebook(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if not book.ebook_file or not book.is_virtual:
        raise Http404("Este libro no está disponible para lectura online")
    
    return render(request, 'read_ebook.html', {'book': book})

def buy_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.book_type == 'physical' and book.stock > 0:
        book.stock -= 1
        book.save()
    return redirect('home')

@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.user == book.uploaded_by or request.user.is_superuser:
        book.delete()
        return redirect('home')
    else:
        # Optionally, add a message for unauthorized deletion attempts
        return redirect('book_detail', book_id=book.id)

@login_required
def payment_screen(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Simulate payment processing
            messages.success(request, '¡Pago realizado con éxito!')
            return redirect('book_detail', book_id=book.id)
    else:
        form = PaymentForm()
    return render(request, 'payment_screen.html', {'form': form, 'book': book})