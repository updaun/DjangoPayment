from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from mall.models import Product
from django.views.generic import ListView


class ProductListView(ListView):
    model = Product
    queryset = Product.objects.all().select_related("category")
    paginate_by = 4

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get("query", "")
        if query:
            qs = qs.filter(name__icontains=query)
        return qs


product_list = ProductListView.as_view()
