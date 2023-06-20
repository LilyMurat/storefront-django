from django.urls import path, include
from . import views

from rest_framework.routers import SimpleRouter
from pprint import pprint

router = SimpleRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)
pprint(router.urls)

# URLConf
#urlpatterns = router.urls

urlpatterns = [
    path('', include(router.urls)),
]


