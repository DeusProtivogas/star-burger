import json
import phonenumbers

from geopy import distance
from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.serializers import CharField

from .models import Product, Restaurant, RestaurantMenuItem
from .models import Order
from .models import OrderElement
from .utility import fetch_coordinates
from .serializers import OrderSerializer, ElementsSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_details = request.data

    with transaction.atomic():
        order_elements = []
        for e in order_details['products']:
            elems_ser = ElementsSerializer(data=e)
            elems_ser.is_valid()
            order_elements.append( elems_ser.save().id )

        order_details['elements'] = order_elements
        serializer = OrderSerializer(data=order_details)
        serializer.is_valid()
        order = serializer.save()

    return Response(serializer.data, status=201)
