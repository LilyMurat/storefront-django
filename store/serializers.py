from rest_framework import serializers
from .models import Product, Collection, Review
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
