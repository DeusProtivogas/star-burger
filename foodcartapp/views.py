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


class ElementsSerializer(ModelSerializer):
    class Meta:
        model = OrderElement
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ElementsSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']


@api_view(['POST'])
def register_order(request):
    my_coords = fetch_coordinates("Красная площадь")

    order_details = request.data


    serializer = OrderSerializer(data=order_details)
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():


        order = Order.objects.create(
            firstname=order_details.get('firstname'),
            lastname=order_details.get('lastname'),
            phonenumber=phonenumbers.parse(order_details.get('phonenumber'), None),
            address=order_details.get('address'),
        )
        restaurants = Restaurant.objects.all()
        order_restaurants = set(restaurants)

        for item in order_details.get('products'):
            product_element = OrderElement.objects.get_or_create(
                product=Product.objects.get(pk=item.get('product')),
                price=Product.objects.get(pk=item.get('product')).price,
                quantity=item.get('quantity'),
                order=order,
            )[0]
            product_element.save()

            element_restaurants = []
            for item in product_element.product.menu_items.all():
                restaurant = restaurants.filter(pk=item.restaurant_id)[0]
                element_restaurants.append(restaurant)

            order_restaurants = order_restaurants.intersection(set(element_restaurants))


        if not order_restaurants:
            order.restaurants_choice = "Нет ресторанов"
        else:
            order.restaurants_choice = f"Доступные рестораны:\n" + '\n'.join(
                [
                    f'{x.name} - {round(distance.distance(my_coords, (x.coordinates.first().latitude, x.coordinates.first().longitude)).km, 2)}'
                    for x in order_restaurants
                ]
            )

        order.save()

    return Response(serializer.data, status=201)
