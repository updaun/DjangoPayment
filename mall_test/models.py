from django.db import models
from uuid import uuid4
from django.core.validators import MinValueValidator
from iamport import Iamport
from django.conf import settings


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        READY = "ready", "미결제"
        PAID = "paid", "결제완료"
        CANCELLED = "cancelled", "결제취소"
        FAILED = "failed", "결제실패"

    uid = models.UUIDField(default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message="1원 이상의 금액을 지정해주세요."),
        ]
    )
    status = models.CharField(
        max_length=9,
        default=StatusChoices.READY,
        choices=StatusChoices.choices,
        db_index=True,
    )
    is_paid_ok = models.BooleanField(default=False, db_index=True)

    @property
    def merchant_uid(self) -> str:
        return self.uid.hex

    def portone_check(self, commit=True):
        api = Iamport(
            imp_key=settings.PORTONE_API_KEY,
            imp_secret=settings.PORTONE_API_SECRET,
        )
        meta = api.find(merchant_uid=self.merchant_uid)
        self.status = meta["status"]
        self.is_paid_ok = meta["status"] == "paid" and meta["amount"] == self.amount

        # TODO: meta 속성을 JSONField로 저장

        if commit:
            self.save()
