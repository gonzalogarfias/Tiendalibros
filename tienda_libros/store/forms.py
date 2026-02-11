from django import forms
from store.models import Book
    

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

class BookUploadForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'description', 'cover_image', 'ebook_file', 'is_virtual']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ebook_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_virtual': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PaymentForm(forms.Form):
    quantity = forms.IntegerField(label='Cantidad', min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    card_number = forms.CharField(label='Número de Tarjeta', max_length=16, min_length=16, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXX XXXX XXXX XXXX'}))
    expiration_date = forms.CharField(label='Fecha de Vencimiento', max_length=5, min_length=5, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/AA'}))
    cvc = forms.CharField(label='CVC', max_length=3, min_length=3, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXX'}))
    card_holder_name = forms.CharField(label='Nombre del Titular', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))