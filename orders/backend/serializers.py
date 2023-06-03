from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from backend.models import Shop, Category, Product, ProductInfo, ProductParameter, Order, OrderItem, Parameter, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     min_length=8)
    email = serializers.EmailField(required=True,
                                   validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    class Meta:
        model = CustomUser
        fields = ['email',
                  'password',
                  'company',
                  'position',
                  'type',
                  'first_name',
                  'last_name']

    def save(self, *args, **kwargs):
        user = CustomUser(email=self.validated_data['email'],
                          company=self.validated_data['company'],
                          position=self.validated_data['position'],
                          type=self.validated_data['type'],
                          first_name=self.validated_data['first_name'],
                          last_name=self.validated_data['last_name'])
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user


class ShopSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                              many=True,
                                              slug_field='name')

    class Meta:
        model = Shop
        fields = ['id', 'name', 'url', 'filename']


class CategorySerializer(serializers.ModelSerializer):

    products = serializers.SlugRelatedField(queryset=Product.objects.all(),
                                            many=True,
                                            slug_field='name')

    class Meta:
        model = Category
        fields = ('id',
                  'name',
                  'products')


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.SlugRelatedField(queryset=Parameter.objects.all(),
                                             slug_field='name')

    class Meta:
        model = ProductParameter
        fields = ['parameter', 'value']


class ProductSerializer1(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id',
                  'name')

class ProductInfoSerializer(serializers.ModelSerializer):

    product = serializers.SlugRelatedField(queryset=Product.objects.all(),
                                           slug_field='name')

    shop = serializers.SlugRelatedField(queryset=Shop.objects.all(),
                                        slug_field='name')
    product_parameters = ProductParameterSerializer(many=True)

    class Meta:
        model = ProductInfo
        fields = ('shop', 'product', 'name', 'product_parameters', 'price', 'price_rrc', 'quantity')


class ProductSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(many=True)

    class Meta:
        model = Product
        fields = ('id',
                  'name',
                  'product_info')

class OrderItemSerializer(serializers.HyperlinkedModelSerializer):
    product_info = serializers.SlugRelatedField(queryset=ProductInfo.objects.all(),
                                           slug_field='name')
    shop = serializers.SlugRelatedField(queryset=Shop.objects.all(),
                                        slug_field='name')
    order = serializers.HyperlinkedRelatedField(queryset=Order.objects.all(),
                                                view_name='orderitem-detail')
    class Meta:
        model = OrderItem
        fields = ['url', 'order', 'product_info', 'shop', 'quantity']


class OrderItemCreateSerializer(serializers.HyperlinkedModelSerializer):

    product_info = serializers.SlugRelatedField(queryset=ProductInfo.objects.all(),
                                           slug_field='name')
    shop = serializers.SlugRelatedField(queryset=Shop.objects.all(),
                                        slug_field='name')

    class Meta:
        model = OrderItem
        fields = ['url', 'product_info', 'shop', 'quantity']


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.SlugRelatedField(queryset=CustomUser.objects.all(),
                                        slug_field='email')
    ordered_items = OrderItemCreateSerializer(many=True, read_only=True)

    def create(self, validated_data):
        instance = Order.objects.create(user=validated_data['user'])
        return instance

    class Meta:
        model = Order
        fields = ['url', 'id', 'user', 'ordered_items', 'status']