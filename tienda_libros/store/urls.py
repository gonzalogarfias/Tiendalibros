from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('sw.js', views.service_worker, name='sw'),

    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('read/<int:book_id>/', views.read_ebook, name='read_ebook'),
    path('subir-libro/', views.upload_book, name='upload_book'),
    path('book/<int:book_id>/delete/', views.delete_book, name='delete_book'),


    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('checkout/', views.view_cart, name='checkout'),
    path('api/cart/add/<int:book_id>/', views.add_to_cart_api, name='add_to_cart'),
    path('confirmar-pago/', views.confirmar_pago, name='confirmar_pago'),
    path('api/cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
