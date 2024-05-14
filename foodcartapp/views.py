import json
import phonenumbers

from django.http import JsonResponse
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.serializers import CharField

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
    # TODO это лишь заглушка

    order_details = request.data

    print("ORDER ", order_details)

    # print(order_details.get('products'))
    # if not order_details.get('products')

    serializer = OrderSerializer(data=order_details)
    serializer.is_valid(raise_exception=True)

    print(serializer.data)

    # if not order_details.get('products'):
    #     return Response({'message': 'Must have list of products',}, status=HTTP_400_BAD_REQUEST)
    #
    # if not len(order_details.get('products')):
    #     return Response({'message': 'List of products cannot be empty'}, status=HTTP_400_BAD_REQUEST)
    #
    # if not isinstance(order_details.get('products'), list):
    #     return Response({'message': 'Must have list of products',}, status=HTTP_400_BAD_REQUEST)
    #
    #
    # if not order_details.get('firstname'):
    #     return Response({'message': 'First name cannot be empty',}, status=HTTP_400_BAD_REQUEST)
    # if not isinstance(order_details.get('firstname'), str):
    #     return Response({'message': 'First name must be string',}, status=HTTP_400_BAD_REQUEST)
    #
    # if not order_details.get('lastname'):
    #     return Response({'message': 'Last name cannot be empty',}, status=HTTP_400_BAD_REQUEST)
    # if not isinstance(order_details.get('lastname'), str):
    #     return Response({'message': 'Last name must be string',}, status=HTTP_400_BAD_REQUEST)
    #
    # if not order_details.get('phonenumber'):
    #     return Response({'message': 'Phone number cannot be empty',}, status=HTTP_400_BAD_REQUEST)
    #
    # if not order_details.get('address'):
    #     return Response({'message': 'Address cannot be empty',}, status=HTTP_400_BAD_REQUEST)
    # if not isinstance(order_details.get('address'), str):
    #     return Response({'message': 'Address must be string',}, status=HTTP_400_BAD_REQUEST)

    # {"products": [{"product": 3, "quantity": 1}], "firstname": "1", "lastname": "2", "phonenumber": "+79624123456", "address": "4"}

    # print("Test ", phonenumbers.parse(order_details.get('phonenumber'), None))
    # print(phonenumbers.is_valid_number(phonenumbers.parse(order_details.get('phonenumber'), None)))

    # if not phonenumbers.is_valid_number(phonenumbers.parse(order_details.get('phonenumber'), None)):
    #     return Response({'message': 'Incorrect phone number',}, status=HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        firstname=order_details.get('firstname'),
        lastname=order_details.get('lastname'),
        # phone=order_details.get('phonenumber'),
        phonenumber=phonenumbers.parse(order_details.get('phonenumber'), None),
        address=order_details.get('address'),
    )
    # print(order)
    # elements = []
    for item in order_details.get('products'):
        product_element = OrderElement.objects.get_or_create(
            product=Product.objects.get(pk=item.get('product')),
            quantity=item.get('quantity'),
            order=order,
        )[0]
        product_element.save()
        # print(element)
        # elements.append(
        #     element[0]
        # )
    # print(elements)

    order.save()

    # for elem in elements:
    #     order.products.add(elem)
    # except AttributeError:
    #     print("Attribute error")
    # except TypeError:
    #     print("Type error")
    # except ObjectDoesNotExist:
    #     return Response({'message': 'Product does not exist',}, status=HTTP_400_BAD_REQUEST)


    return Response(serializer.data, status=201)
