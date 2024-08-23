from django.shortcuts import render


def payment_view(request):
    return render(request, "mall_test/payment_form.html")
