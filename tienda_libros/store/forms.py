from django import forms
from store.models import Book
import os
    

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

class BookUploadForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'description', 'cover_image', 'ebook_file', 'is_virtual', 'stock']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ebook_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.epub'}),
            'is_virtual': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'isVirtualCheck'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def clean_ebook_file(self):
        file = self.cleaned_data.get('ebook_file')
        is_virtual = self.cleaned_data.get('is_virtual')

        if is_virtual and file:
            extension = os.path.splitext(file.name)[1].lower()
            if extension != '.epub':
                raise ValidationError("Para libros virtuales, solo se permiten archivos en formato .epub por seguridad del autor.")
        
        return file

    def clean(self):
        cleaned_data = super().clean()
        is_virtual = cleaned_data.get('is_virtual')
        stock = cleaned_data.get('stock')

        if not is_virtual and (stock is None or stock <= 0):
            self.add_error('stock', "Los libros físicos deben tener un stock mayor a 0.")
        
        return cleaned_data

class PaymentForm(forms.Form):
    quantity = forms.IntegerField(label='Cantidad', min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    card_number = forms.CharField(label='Número de Tarjeta', max_length=16, min_length=16, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXX XXXX XXXX XXXX'}))
    expiration_date = forms.CharField(label='Fecha de Vencimiento', max_length=5, min_length=5, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/AA'}))
    cvc = forms.CharField(label='CVC', max_length=3, min_length=3, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXX'}))
    card_holder_name = forms.CharField(label='Nombre del Titular', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    