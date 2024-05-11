import json
import phonenumbers

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view

from .models import Product
from .models import Order
from .models import OrderElement


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
    # TODO это лишь заглушка
    order_details = request.data

    print("ORDER ", order_details)

    # {"products": [{"product": 3, "quantity": 1}], "firstname": "1", "lastname": "2", "phonenumber": "+79624123456", "address": "4"}

    print("Test ", phonenumbers.parse(order_details.get('phonenumber'), None))
    print(phonenumbers.is_possible_number(phonenumbers.parse(order_details.get('phonenumber'), None)))

    if not phonenumbers.is_possible_number(phonenumbers.parse(order_details.get('phonenumber'), None)):
        raise TypeError

    order = Order.objects.create(
        name=order_details.get('firstname'),
        surname=order_details.get('lastname'),
        # phone=order_details.get('phonenumber'),
        phone=phonenumbers.parse(order_details.get('phonenumber'), None),
        address=order_details.get('address'),
    )
    print(order)
    # elements = []
    for item in order_details.get('products'):
        element = OrderElement.objects.get_or_create(
            element=Product.objects.get(pk=item.get('product')),
            quantity=item.get('quantity'),
            order=order,
        )[0]
        element.save()
        # print(element)
        # elements.append(
        #     element[0]
        # )
    # print(elements)

    order.save()

    # for elem in elements:
    #     order.products.add(elem)

    return JsonResponse({})
