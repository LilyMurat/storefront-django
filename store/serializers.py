from rest_framework import serializers
from .models import Product, Collection
from decimal import Decimal

class CollectionSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Collection
        fields = ['id', 'title','products_count']

    products_count = serializers.IntegerField()
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length = 255)


 
class ProductSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Product 
        fields = [ 'id', 'slug','inventory','title','unit_price', 'price_with_tax', 'collection']
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    # price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    # collection = serializers.HyperlinkedRelatedField(
    #    queryset=Collection.objects.all() , 
    #    view_name='collection-detail'
    # )

    def calculate_tax(self, product: Product):
        result = Decimal(f'{product.unit_price * Decimal(1.13):.2f}')
        return result
    
    #for validating password passowrd == confirm password 
    # def validate(self, data):
    #     if data['password'] != data['confirm_password']:
    #         return serializers.ValidationError("Password didn't match!")
    #     return data


    #to create new product object 
    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     product.other = 1
    #     product.save()
    #     return product
    
    #to update 
    # def update (self, instance, validated_data):
    #     instance.unit_price = validated_data.get('unit_price')
    #     instance.save()
    #     return instance
