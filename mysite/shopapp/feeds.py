from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy

from .models import Product


class LatestProductsFeed(Feed):
    title = "Latest products"
    link = reverse_lazy("shopapp:products-list")
    description = "Updates on new products"

    def items(self):
        return Product.objects.order_by("-created_at")[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return reverse_lazy(
            "shopapp:product-details",
            args=[item.pk],
        )