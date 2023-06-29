from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from .models import Product, Collection, OrderItem, Review, Cart, CartItem, Customer, Order
from .serializers import CreateOrderSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer,\
      CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer,\
          CustomerSerializer, OrderSerializer
from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadonly, FUllDjangoModelPermissons

# Create your views here.

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends=[DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadonly]
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
    permission_classes = [IsAdminOrReadonly]

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count()>0:
            return Response({'error':'Collection cannot be deleted because it contains a product'})
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin,GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    
class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method =='POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    
    def get_queryset(self):
        return CartItem.objects\
            .filter(cart_id=self.kwargs['cart_pk'])\
            .select_related('product')
    
class CustomerViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True)
    def hsitory(self, request, pk):
        return Response('ok')



    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        if request.method == 'GET':
            (customer, created) = Customer.objects.get(user_id=request.user.id)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    #permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_serializer_context(self):
        return {'user_id':self.request.user.id}

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()
        
        customer_id= Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)
        
