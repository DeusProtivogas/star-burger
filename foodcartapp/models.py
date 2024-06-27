from datetime import datetime

from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.functions import Now
from phonenumber_field.modelfields import PhoneNumberField

class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name



class OrderElement(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='элемент',
        related_name='elements',
        null=False,
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField(
        'количество',
        null=False,
        blank=False,
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        'стоимость',
        max_digits=8,
        decimal_places=2,
        null=False,
        blank=False,
        validators=[MinValueValidator(0)],
    )
    # order = models.ForeignKey(
    #     Order,
    #     verbose_name='заказ',
    #     related_name='elements',
    #     on_delete=models.CASCADE,
    # )

    class Meta:
        verbose_name = 'элемент'
        verbose_name_plural = 'элементы'

    def __str__(self):
        return f"{self.product.name}: {self.quantity}"


class Order(models.Model):
    RECEIVED = 'received'
    ACCEPTED = 'accepted'
    INPROGRESS = 'in_progress'
    DELIVERY = 'being_delivered'
    DONE = 'delivered'
    ORDER_STATUSES = [
        (RECEIVED, 'Начат'),
        (ACCEPTED, 'Принят'),
        (INPROGRESS, 'Собирается'),
        (DELIVERY, 'В доставке'),
        (DONE, 'Выполнен'),
    ]
    CASH = 'cash'
    CARD = 'card'
    PAYMENT_METHODS = [
        (CASH, 'Наличными'),
        (CARD, 'Электронно'),
    ]

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUSES,
        default=RECEIVED,
        db_index=True,
    )
    payment = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default=CASH,
        db_index=True,
    )
    firstname = models.CharField(
        'имя',
        max_length=50,
        blank=False,
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50,
        blank=False,
    )
    address = models.TextField(
        'адрес',
        max_length=200,
        blank=False,
    )
    phonenumber = PhoneNumberField(
        'телефон',
        null=False,
    )
    comment = models.TextField(
        'комментарий',
        blank=True,
    )
    received = models.DateTimeField(
        'поступил в',
        default=datetime.now,
        blank=True,
    )
    confirmed = models.DateTimeField(
        'уточнен в',
        blank=True,
        null=True,
    )
    delivered = models.DateTimeField(
        'доставлен в',
        blank=True,
        null=True,
    )
    restaurant_chosen = models.ForeignKey(
        Restaurant,
        verbose_name='Где готовить',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    restaurants_choice = models.TextField(
        verbose_name='Варианты ресторанов',
        max_length=200,
        blank=True,
    )
    elements = models.ManyToManyField(
        OrderElement,
        verbose_name='Элементы',
        related_name='order',
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"№{self.pk}: {self.firstname} {self.lastname}"



class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Coordinates(models.Model):
    address = models.TextField(
        'адрес текстом',
    )
    longitude = models.DecimalField(
        'долгота',
        max_digits=14,
        decimal_places=10,
    )
    latitude = models.DecimalField(
        'широта',
        max_digits=14,
        decimal_places=10,
    )
    last_updated = models.DateTimeField(
        'обновлялись в',
        blank=True,
        null=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='coordinates',
        verbose_name='ресторан',
    )

    class Meta:
        verbose_name = 'адрес'
        verbose_name_plural = 'адреса'

    def __str__(self):
        return f"{self.restaurant}: {self.longitude} {self.latitude}"
