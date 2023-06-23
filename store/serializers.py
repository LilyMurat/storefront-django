from rest_framework import serializers
from .models import Product, Collection, Review, Cart, CartItem
from decimal import Decimal

class CollectionSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Collection
        fields = ['id', 'title','products_count']

    products_count = serializers.IntegerField(read_only=True)
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length = 255)


 
class ProductSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Product 
        fields = [ 'id', 'slug','inventory','title','unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        result = Decimal(f'{product.unit_price * Decimal(1.13):.2f}')
        return result

class ReviewSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)
    
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Product
        fields = ['id', 'title', 'unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_itme:CartItem):
        return cart_itme.quantity * cart_itme.unit_price
    
    class Meta:
        model = CartItem
        fields = ['id', 'product','quantity', 'total_price']

class UpdateCartItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['quantity']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id','items', 'total_price']

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given ID was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try: 
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id= product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
            #update an existing item 
        except CartItem.DoesNotExist:
            #create a new item
            self.instance = CartItem.objects.create(cart_id = cart_id, **self.validated_data)
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']
