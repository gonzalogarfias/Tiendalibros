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
from django.http import HttpResponse, Http404
from django.contrib.staticfiles import finders

from .forms import BookUploadForm, ContactForm, PaymentForm
from .models import Book, CartItem, Cart


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
    sw_path = finders.find('js/sw.js') 
    
    if not sw_path:
        raise Http404("Archivo sw.js no encontrado en static/js/")

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
def update_cart_item(request, item_id):
    items_list = []
    
    if request.method == 'POST':
        try:
            cart = get_object_or_404(Cart, user=request.user)
            data = json.loads(request.body)
            action = data.get('action')
            item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

            if action == 'add':
                if not item.book.is_virtual and item.quantity >= item.book.stock:
                    return JsonResponse({'status': 'error', 'message': 'Sin stock suficiente'}, status=400)
                item.quantity += 1
                item.save()
            elif action == 'remove':
                item.quantity -= 1
                if item.quantity <= 0:
                    item.delete()
                else:
                    item.save()

            for i in cart.items.all():
                items_list.append({
                    'id': i.id,
                    'book_title': i.book.title,
                    'book_price': str(i.book.price),
                    'quantity': i.quantity,
                    'total_item': str(i.total_price())
                })

            return JsonResponse({
                'status': 'success',
                'items': items_list,
                'cart_total': str(cart.total_price())
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@login_required
def add_to_cart_api(request, book_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=401)

    if request.method == 'POST':
        cart, created = Cart.objects.get_or_create(user=request.user)
        book = Book.objects.get(id=book_id)
        
        item, item_created = CartItem.objects.get_or_create(cart=cart, book=book)
        
        if not item_created:
            item.quantity += 1
            item.save()
        total_items = sum(item.quantity for item in cart.items.all())
        
        return JsonResponse({
            'status': 'success',
            'message': f'"{book.title}" añadido al carrito',
            'total_items': total_items
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
