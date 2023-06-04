from django.core.validators import URLValidator
from django.http import JsonResponse
import requests
from rest_framework import status, viewsets, generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from yaml import load as load_yaml, Loader

from backend.models import Shop, Category, Product, ProductInfo, ProductParameter, Parameter, Order, OrderItem, CustomUser
from backend.serializers import ProductInfoSerializer, OrderSerializer, OrderItemSerializer, CustomUserSerializer
from django.core.mail import send_mail
import orders.settings


class RegisterUserView(generics.CreateAPIView):

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)

        data = {}

        if serializer.is_valid():
            serializer.save()
            data['response'] = True
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = serializer.errors

            return Response(data)


class PartnerUpdate(APIView):

    def yaml_uploader(self, request, stream):

        data = load_yaml(stream, Loader=Loader)
        shop, _ = Shop.objects.get_or_create(name=data['shop'])
        for category in data['categories']:
            category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()
        ProductInfo.objects.filter(shop=shop.id).delete()
        for item in data['goods']:
            product, _ = Product.objects.get_or_create(name=item['model'], category_id=item['category'])
            product_info = ProductInfo.objects.create(product=product,
                                                      name=item['name'],
                                                      price=item['price'],
                                                      price_rrc=item['price_rrc'],
                                                      quantity=item['quantity'],
                                                      shop=shop)
            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(product_info=product_info,
                                                parameter=parameter_object,
                                                value=value)

        return JsonResponse({'Status': True})

    def post(self, request, *args, **kwargs):

        url = request.data.get('url')
        filename = request.data.get('filename')

        if url:
            url = request.data.get('url')
            validate_url = URLValidator
            try:
                validate_url(url)
            except ValidationError as err:
                return JsonResponse({'Status': False, 'Error': str(err)})

        if filename:
            with open(filename, 'r', encoding='utf-8') as stream:
                return self.yaml_uploader(request=request, stream=stream)

        else:
            return JsonResponse({'Status': False, 'Errors': 'Каталог магазина отсутствует'})


class ProductInfoViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer


class OrderViewSet(viewsets.ModelViewSet):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, ordered_items=[])


class OrderItemViewSet(viewsets.ModelViewSet):

    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def post(self, request):
        serializer = OrderItemSerializer(data=request.data,
                                         context={'request': request})
        if serializer.is_valid():
            serializer.save()
            order = serializer.data['order']
            user = serializer.context['request'].user
            send_mail(subject='Произошло обновление заказа',
                      message=f'Ваш заказ {order} был изменен.',
                      from_email=orders.settings.EMAIL_HOST_USER,
                      recipient_list=[user])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        order = serializer.data['order']
        user = serializer.context['request'].user
        send_mail(subject='Произошло обновление заказа',
                  message=f'Ваш заказ {order} был изменен.',
                  from_email=orders.settings.EMAIL_HOST_USER,
                  recipient_list=[user])
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        order = serializer.data['order']
        user = serializer.context['request'].user
        send_mail(subject='Произошло обновление заказа',
                  message=f'Ваш {order} заказ был изменен.',
                  from_email=orders.settings.EMAIL_HOST_USER,
                  recipient_list=[user])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
