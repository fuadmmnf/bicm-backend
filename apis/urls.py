# basic URL Configurations
from django.urls import include, path
# import routers
from rest_framework import routers

# import everything from views
from .views import *

# define the router
router = routers.DefaultRouter()

# define the router path and viewset to be used

# specify URL Path for rest_framework
urlpatterns = [
    path('volumes/', sector_wise_volumes),
    path('returns/', sector_wise_return),
    path('api-auth/', include('rest_framework.urls'))
]
