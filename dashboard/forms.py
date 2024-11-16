from django import forms
from .models import Product, Batch, WritenOff


class CreateProduct(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'code', 'category', 'price']

class CreateBatch(forms.ModelForm):

    class Meta:
        model = Batch
        fields = ['product', 'quantity', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

class UpdateBatch(forms.ModelForm):

    class Meta:
        model = Batch
        fields = ['product', 'quantity', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

class WriteOffProduct(forms.ModelForm):

    class Meta:
        model = WritenOff
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        self.batch = kwargs.pop('batch', None) 
        super().__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if self.batch and quantity > self.batch.left:
            raise forms.ValidationError(f"Cannot write off more than available quantity ({self.batch.left})")
        return quantity