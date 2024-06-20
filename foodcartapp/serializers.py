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
        # print('elem data in ser ', data)
        # print(Product.objects.get(pk=data.get('product')).price)

        with transaction.atomic():
            product_element = OrderElement.objects.create(
                product=data.get('product'),
                price=data.get('product').price,
                # price=data.get('product').price,
                quantity=data.get('quantity'),
                order=data.get('order'),
            )


            product_element.save()
        return product_element

    class Meta:
        model = OrderElement
        fields = ['product', 'quantity', 'price', 'order']


class OrderSerializer(ModelSerializer):
    # products = ElementsSerializer(many=True, allow_empty=True, required=False)

    def create(self, order_details):
        print('dets ', order_details)
        product_list = order_details.get('products')
        print(product_list)

        with transaction.atomic():
            order = Order.objects.create(
                firstname=order_details.get('firstname'),
                lastname=order_details.get('lastname'),
                phonenumber=phonenumbers.parse(order_details.get('phonenumber'), None),
                address=order_details.get('address'),
                restaurants_choice="Нет ресторанов",
            )
            print("AAAA")

            # for product in product_list:
            #     print('b')
            #     product_data = {
            #         'order': order,
            #         'product': product.get('product'),
            #         'quantity': product.get('quantity'),
            #     }
            #     product_element = ElementsSerializer(data=product_data)
            #     print(product_element)
            #
            #
            #
            # restaurants = Restaurant.objects.all()
            # order_restaurants = set(restaurants)
            #
            # if not order_restaurants:
            #     order.restaurants_choice = "Нет ресторанов"
            # else:
            #     order.restaurants_choice = f"Доступные рестораны:\n" + '\n'.join(
            #         [
            #             f'{x.name} - {round(distance.distance(fetch_coordinates(), (x.coordinates.first().latitude, x.coordinates.first().longitude)).km, 2)}'
            #             for x in order_restaurants
            #         ]
            #     )

            order.save()

        return order

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address']
