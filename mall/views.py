from django.forms import modelformset_factory
from django.shortcuts import render
from mall.models import Product, CartProduct, Order, OrderPayment
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from mall.forms import CartProductForm
from django.views.decorators.http import require_POST
from django.http import HttpResponse


class ProductListView(ListView):
    model = Product
    queryset = Product.objects.filter(status=Product.Status.ACTIVE).select_related(
        "category"
    )
    paginate_by = 4

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get("query", "")
        if query:
            qs = qs.filter(name__icontains=query)
        return qs


product_list = ProductListView.as_view()


@login_required
def cart_detail(request):
    cart_product_qs = (
        CartProduct.objects.filter(user=request.user)
        .select_related("product")
        .order_by("product__name")
    )

    CartProductFormset = modelformset_factory(
        model=CartProduct,
        form=CartProductForm,
        can_delete=True,
        extra=0,
    )
    if request.method == "POST":
        formset = CartProductFormset(
            data=request.POST,
            queryset=cart_product_qs,
        )
        if formset.is_valid():
            formset.save()
            messages.success(request, "장바구니를 업데이트했습니다.")
            return redirect("cart_detail")
    else:
        formset = CartProductFormset(queryset=cart_product_qs)

    return render(
        request,
        "mall/cart_detail.html",
        {
            "formset": formset,
        },
    )


@login_required
@require_POST
def add_to_cart(request, product_pk):
    product_qs = Product.objects.filter(status=Product.Status.ACTIVE)
    product = get_object_or_404(product_qs, pk=product_pk)
    quantity = int(request.GET.get("quantity", 1))

    cart_product, is_created = CartProduct.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": quantity},
    )

    if not is_created:
        cart_product.quantity += quantity
        cart_product.save()

    # messages.success(request, "장바구니에 추가했습니다.")

    # redirect_url = request.META.get("HTTP_REFERER", "product_list")

    # return redirect(redirect_url)
    return HttpResponse("ok")


@login_required
def order_new(request):
    cart_product_qs = CartProduct.objects.filter(user=request.user)
    order = Order.create_from_cart(request.user, cart_product_qs)
    cart_product_qs.delete()
    return redirect("order_pay", order.pk)


@login_required
def order_pay(request, pk):
    order = get_object_or_404(Order, pk=pk)
    messages.warning(request, "구현 예정")

    if not order.can_pay():
        messages.error(request, "결제할 수 없는 주문입니다.")
        return redirect("order_detail", order.pk)

    payment = OrderPayment.create_by_order(order)

    return render(request, "mall/order_pay.html", {"payment": payment})
