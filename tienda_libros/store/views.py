import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.views.decorators.cache import cache_control

from .forms import BookUploadForm, ContactForm, PaymentForm
from .models import Book, CartItem, Cart


# --- GENERAL / PÚBLICO ---

def home(request):
    tipo = request.GET.get('tipo')  
    if tipo == 'virtual':
        books = Book.objects.filter(is_virtual=True)
    elif tipo == 'fisico':
        books = Book.objects.filter(is_virtual=False)
    else:
        books = Book.objects.all()  
    
    return render(request, 'books/home.html', {
        'books': books,
        'tipo_actual': tipo  
    })

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
            return render(request, 'contact/contact.html', {'form': form, 'success': True})
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})

@cache_control(max_age=86400)
def service_worker(request):
    sw_path = finders.find('service-worker.js')
    with open(sw_path, 'rb') as f:
        return HttpResponse(f.read(), content_type='application/javascript')


# --- GESTIÓN DE LIBROS ---

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    already_bought = request.session.get(f"bought_{book.id}", False)
    
    return render(request, 'books/book_detail.html', {
        'book': book,
        'already_bought': already_bought
    })

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
    return render(request, 'books/upload_book.html', {'form': form})

@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.user == book.uploaded_by or request.user.is_superuser:
        book.delete()
        return redirect('home')
    return redirect('book_detail', book_id=book.id)

def read_ebook(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if not book.ebook_file or not book.is_virtual:
        raise Http404("Este libro no está disponible para lectura online")
    return render(request, 'books/read_ebook.html', {'book': book})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total = sum(item.book.price * item.quantity for item in items)
    
    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'items': items,
        'total_del_carrito': total
    })

@login_required
def add_to_cart_api(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    total_items = CartItem.objects.filter(cart=cart).count()
    return JsonResponse({
        'success': True, 
        'message': f'"{book.title}" se agregó al carrito',
        'cart_count': total_items
    })

@csrf_exempt
def confirmar_pago(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('orderID')
            cart = Cart.objects.get(user=request.user)
            items = CartItem.objects.filter(cart=cart)
            
            for item in items:
                libro = item.book
                if not libro.is_virtual and libro.stock >= item.quantity:
                    libro.stock -= item.quantity
                    libro.save()
                request.session[f"bought_{libro.id}"] = True
            
            items.delete()
            return JsonResponse({'status': 'success', 'order_id': order_id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)

@login_required
def payment_screen(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            messages.success(request, '¡Pago realizado con éxito!')
            return redirect('book_detail', book_id=book.id)
    else:
        form = PaymentForm()
    return render(request, 'cart/payment_screen.html', {'form': form, 'book': book})
