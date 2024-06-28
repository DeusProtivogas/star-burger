import phonenumbers

from geopy import distance
from django.db import transaction
from rest_framework.serializers import ModelSerializer

from .models import Order
from .models import Product
from .models import Restaurant
from .models import OrderElement
from .utility import fetch_coordinates


class ElementsSerializer(ModelSerializer):

    def create(self, data):

        with transaction.atomic():
            product_element = OrderElement.objects.create(
                product=data.get('product'),
                price=data.get('product').price,
                quantity=data.get('quantity'),
            )

        return product_element

    class Meta:
        model = OrderElement
        fields = ['product', 'quantity',]


class OrderSerializer(ModelSerializer):

    def create(self, order_details):
        element_list = order_details.get('elements')

        with transaction.atomic():
            order = Order.objects.create(
                firstname=order_details.get('firstname'),
                lastname=order_details.get('lastname'),
                phonenumber=phonenumbers.parse(order_details.get('phonenumber'), None),
                address=order_details.get('address'),
                restaurants_choice="Нет ресторанов",
            )
            order.elements.add( *element_list )

            restaurants = Restaurant.objects.all()
            order_restaurants = set(restaurants)
            element_restaurants = []
            for item in order.elements.all():
                for possible_restaurant in item.product.menu_items.all():
                    restaurant = restaurants.filter(pk=possible_restaurant.restaurant.id)[0]
                    element_restaurants.append(restaurant)

            order_restaurants = order_restaurants.intersection(set(element_restaurants))

            if order_restaurants:
                order.restaurants_choice = f"Доступные рестораны:\n" + '\n'.join(
                    [
                        f'{x.name} - {round(distance.distance(fetch_coordinates(), (x.coordinates.first().latitude, x.coordinates.first().longitude)).km, 2)}'
                        for x in order_restaurants
                    ]
                )
            order.save()

        return order

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'elements']
