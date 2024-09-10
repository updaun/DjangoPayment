from typing import List
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import UniqueConstraint, QuerySet
from uuid import uuid4
from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = verbose_name_plural = "상품 분류"


class Product(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "a", "정상"
        SOLD_OUT = "s", "품절"
        OBSOLETE = "o", "단종"
        INACTIVE = "i", "비활성화"

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField()
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.INACTIVE,
    )
    photo = models.ImageField(upload_to="mall/product/photo/%Y/%m/%d")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<{self.pk}> {self.name}"

    class Meta:
        verbose_name = verbose_name_plural = "상품"
        ordering = ["-pk"]


class CartProduct(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name="cart_product_set",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    def __str__(self):
        return f"<{self.pk}> {self.product.name} x {self.quantity}"

    @property
    def amount(self):
        return self.product.price * self.quantity

    class Meta:
        verbose_name_plural = verbose_name = "장바구니 상품"
        constraints = [
            UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product",
            ),
        ]


class Order(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "주문요청"
        FAILED_PAYMENT = "failed_payment", "결제실패"
        PAID = "paid", "결제완료"
        PREPARED_PRODUCT = "prepared_product", "상품준비중"
        SHIPPED = "shipped", "배송중"
        DELIVERED = "delivered", "배송완료"
        CANCELED = "canceled", "주문취소"

    uid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    total_amount = models.PositiveIntegerField("결제금액")
    status = models.CharField(
        "진행상태",
        choices=Status.choices,
        default=Status.REQUESTED,
        max_length=20,
        db_index=True,
    )
    product_set = models.ManyToManyField(
        Product,
        through="OrderedProduct",
        blank=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_from_cart(
        cls, user: User, cart_product_qs: QuerySet[CartProduct]
    ) -> "Order":
        cart_product_list: List[CartProduct] = list(cart_product_qs)
        total_amount = sum(cart_product.amount for cart_product in cart_product_list)
        order = cls.objects.create(
            user=user,
            total_amount=total_amount,
        )

        ordered_product_list = []
        for cart_product in cart_product_list:
            product = cart_product.product
            ordered_product = OrderedProduct(
                order=order,
                product=product,
                name=product.name,
                price=product.price,
                quantity=cart_product.quantity,
            )
            ordered_product_list.append(ordered_product)
        OrderedProduct.objects.bulk_create(ordered_product_list)
        return order


class OrderedProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_constraint=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_constraint=False)
    name = models.CharField("상품명", max_length=100, help_text="주문 시점의 상품평을 저장합니다.")
    price = models.PositiveIntegerField("가격", help_text="주문 시점의 가격을 저장합니다.")
    quantity = models.PositiveIntegerField("수량")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
