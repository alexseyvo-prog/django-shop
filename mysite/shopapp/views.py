from timeit import default_timer

from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .forms import ProductForm
from .models import Product, Order, ProductImage

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .serializers import OrderSerializer, ProductSerializer

from django.contrib.syndication.views import Feed

from django.contrib.auth import get_user_model
from django.core.cache import cache
import random

class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
        }
        return render(request, 'shopapp/shop-index.html', context=context)


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy("shopapp:products_list")


class ProductUpdateView(UpdateView):
    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )

        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by('pk').all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
            }
            for product in products
        ]
        return JsonResponse({"products": products_data})


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]
    search_fields = [
        "name",
        "description",
    ]
    ordering_fields = [
        "id",
        "name",
        "price",
        "created_at",
    ]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_fields = [
        "user",
        "promocode",
    ]
    ordering_fields = [
        "id",
        "created_at",
    ]


class LatestProductsFeed(Feed):
    title = "Latest products"
    description = "Updates on latest products"
    link = "/shop/products/"

    def items(self):
        return Product.objects.order_by("-created_at")[:5]

    def item_title(self, item: Product) -> str:
        return item.name

    def item_description(self, item: Product) -> str:
        return item.description

    def item_link(self, item: Product) -> str:
        return item.get_absolute_url()


User = get_user_model()


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/user_orders_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        self.owner = get_object_or_404(
            User,
            pk=self.kwargs["user_id"],
        )

        return Order.objects.filter(
            user=self.owner,
        ).select_related(
            "user",
        ).prefetch_related(
            "products",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        context["random_number"] = random.randint(1, 1000)
        context["cached_random_number"] = random.randint(1, 1000)
        return context



def user_orders_export(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    cache_key = f"user_orders_export_{user_id}"
    cached_orders = cache.get(cache_key)

    if cached_orders is not None:
        return JsonResponse(
            cached_orders,
            safe=False,
        )

    orders = (
        Order.objects
        .filter(user=user)
        .order_by("pk")
    )

    serializer = OrderSerializer(
        orders,
        many=True,
    )

    orders_data = serializer.data

    cache.set(
        cache_key,
        orders_data,
        timeout=300,
    )

    return JsonResponse(
        orders_data,
        safe=False,
    )


def user_orders_export(request, user_id):
    cache_key = f"user_orders_export_{user_id}"
    cached_orders = cache.get(cache_key)

    if cached_orders is not None:
        return JsonResponse(
            cached_orders,
            safe=False,
        )

    user = get_object_or_404(User, pk=user_id)

    orders = (
        Order.objects
        .filter(user=user)
        .order_by("pk")
    )

    serializer = OrderSerializer(
        orders,
        many=True,
    )

    orders_data = serializer.data

    cache.set(
        cache_key,
        orders_data,
        timeout=300,
    )

    return JsonResponse(
        orders_data,
        safe=False,
    )