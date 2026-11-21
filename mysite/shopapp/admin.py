import csv
import io

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path

from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm
from .models import Order, Product, ProductImage


class OrderInline(admin.TabularInline):
    model = Product.orders.through


class ProductInline(admin.StackedInline):
    model = ProductImage


class OrderProductsInline(admin.StackedInline):
    model = Order.products.through


@admin.action(description="Archive products")
def mark_archived(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet,
):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet,
):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]
    list_display = (
        "pk",
        "name",
        "description_short",
        "price",
        "discount",
        "archived",
    )
    list_display_links = ("pk", "name")
    ordering = ("-name", "pk")
    search_fields = ("name", "description")

    fieldsets = [
        (
            None,
            {
                "fields": ("name", "description"),
            },
        ),
        (
            "Price options",
            {
                "fields": ("price", "discount"),
                "classes": ("wide", "collapse"),
            },
        ),
        (
            "Images",
            {
                "fields": ("preview",),
            },
        ),
        (
            "Extra options",
            {
                "fields": ("archived",),
                "classes": ("collapse",),
                "description": (
                    "Extra options. Field 'archived' is for soft delete"
                ),
            },
        ),
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "admin/shopapp/orders_changelist.html"
    inlines = [
        OrderProductsInline,
    ]
    list_display = (
        "delivery_address",
        "promocode",
        "created_at",
        "user_verbose",
    )

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv),
                name="shopapp_order_import_csv",
            ),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "GET":
            form = CSVImportForm()
            return render(
                request,
                "admin/shopapp/csv_form.html",
                {"form": form},
            )

        form = CSVImportForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(
                request,
                "admin/shopapp/csv_form.html",
                {"form": form},
            )

        csv_file = form.cleaned_data["csv_file"]
        decoded_file = csv_file.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(decoded_file))

        for row in reader:
            order, _ = Order.objects.get_or_create(
                pk=row["order_id"],
                defaults={
                    "user": request.user,
                },
            )

            product = Product.objects.get(pk=row["product_id"])
            order.products.add(product)

        self.message_user(
            request,
            "Заказы успешно импортированы.",
        )
        return redirect("admin:shopapp_order_changelist")