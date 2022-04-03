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
    path('monthly-indices-dsex/', get_dsex_monthly_indices),
    path('monthly-indices-dses/', get_dses_monthly_indices),
    path('monthly-indices-ds30/', get_ds30_monthly_indices),
    path('monthly-indices-cdset/', get_cdset_monthly_indices),
    path('daily-indices-dsex/', get_dsex_daily_indices),
    path('daily-indices-dses/', get_dses_daily_indices),
    path('daily-indices-ds30/', get_ds30_daily_indices),
    path('daily-indices-cdset/', get_cdset_daily_indices),
    path('monthly-market-aggregates/', get_avg_market_aggregate),
    path('ad-ratios/', get_all_ad_ratio),
    path('todays-advance-decline-neutral/', get_todays_adn),
    path('todays-trade-value-volume/', get_todays_tvv),
    path('api-auth/', include('rest_framework.urls'))
]
