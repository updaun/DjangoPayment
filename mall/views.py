from django.shortcuts import render
from mall.models import Product
from django.views.generic import ListView


class ProductListView(ListView):
    model = Product
    queryset = Product.objects.all().select_related("category")
    paginate_by = 4


product_list = ProductListView.as_view()
