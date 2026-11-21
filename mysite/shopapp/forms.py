from django import forms

from shopapp.models import Product


class ProductForm(forms.ModelForm):
    images = forms.ImageField()

    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV-файл с заказами",
        help_text=(
            "Файл должен содержать заголовки: "
            "order_id, product_id, quantity"
        ),
    )