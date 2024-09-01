import requests
from django.core.management import BaseCommand
from dataclasses import dataclass
from mall.models import Category, Product
from django.core.files.base import ContentFile
from tqdm import tqdm


BASE_URL = "https://raw.githubusercontent.com/pyhub-kr/dump-data/main/django-shopping-with-iamport/"


@dataclass
class Item:
    category_name: str
    name: str
    price: int
    priceUnit: str
    desc: str
    photo_path: str


class Command(BaseCommand):
    help = "Load products from JSON file"

    def handle(self, *args, **options):
        json_url = BASE_URL + "product-list.json"
        item_dict_list = requests.get(json_url).json()

        item_list = [Item(**item_dict) for item_dict in item_dict_list]
        category_name_set = {item.category_name for item in item_list}

        category_dict = {}
        for category_name in category_name_set:
            category, _ = Category.objects.get_or_create(name=category_name or "미분류")
            category_dict[category.name] = category

        for item in tqdm(item_list):
            category: Category = category_dict[item.category_name or "미분류"]
            product, is_created = Product.objects.get_or_create(
                category=category,
                name=item.name,
                defaults={
                    "description": item.desc,
                    "price": item.price,
                },
            )
            if is_created:
                photo_url = BASE_URL + item.photo_path
                file_name = photo_url.rsplit("/", 1)[-1]
                photo_data = requests.get(photo_url).content
                product.photo.save(
                    name=file_name,
                    content=ContentFile(photo_data),
                    save=True,
                )
