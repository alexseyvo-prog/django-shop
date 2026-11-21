from django.contrib import admin

from .models import Article, Author, Category, Tag


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "pub_date",
    )
    filter_horizontal = (
        "tags",
    )


admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Tag)