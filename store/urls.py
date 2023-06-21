from django.urls import path, include
from . import views

#from rest_framework.routers import SimpleRouter
from pprint import pprint

from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
#router.register('reviews',views.ReviewViewSet)
pprint(router.urls)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

# URLConf
urlpatterns = router.urls + products_router.urls



