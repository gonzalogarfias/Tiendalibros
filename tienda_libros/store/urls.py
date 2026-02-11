from django.conf import settings
from django.urls import include, path
from django.contrib.auth import views as auth_views
from .views import book_detail, buy_book, contact, home, read_ebook, upload_book, register, delete_book, payment_screen
from django.conf.urls.static import static


urlpatterns = [
    path('', home, name='home'),
    path('contact/', contact, name='contact'),
    path('book/<int:book_id>/', book_detail, name='book_detail'),
    path('read/<int:book_id>/', read_ebook, name='read_ebook'),
    path('subir-libro/', upload_book, name='upload_book'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('book/<int:book_id>/delete/', delete_book, name='delete_book'),
    path('book/<int:book_id>/buy/', payment_screen, name='payment_screen'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)