from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin
from .models import Product, Collection, OrderItem, Review, Cart
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer
from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from .pagination import DefaultPagination

# Create your views here.

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends=[DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price','last_update' ]

    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error':'Product cannot be deleted because it associated with an order item.'})
        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet): 
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class =CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        if Collection.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error':'Collection cannot be deleted because it contains a product'})
        return super().destroy(request, *args, **kwargs)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}
    
"""
    def destroy(self, request, *args, **kwargs):
        if Review.objects.filter(product_id=kwargs['pk']).count() >0:
            return Response({'error':'Review cannot be deleted because the review is for that particular product only '})
        return super().destroy(request, *args, **kwargs)
"""

class CartViewSet(CreateModelMixin, GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


 