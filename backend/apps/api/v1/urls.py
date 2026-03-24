from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.views import UserViewSet
from apps.operators.views import OperatorTypeViewSet, OperatorViewSet
from apps.indicators.views import IndicatorCategoryViewSet, IndicatorViewSet, PeriodViewSet
from apps.data_entry.views import DataEntryViewSet, CumulativeDataViewSet, FileUploadViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'operator-types', OperatorTypeViewSet, basename='operator-type')
router.register(r'operators', OperatorViewSet, basename='operator')
router.register(r'indicator-categories', IndicatorCategoryViewSet, basename='indicator-category')
router.register(r'indicators', IndicatorViewSet, basename='indicator')
router.register(r'periods', PeriodViewSet, basename='period')
router.register(r'data', DataEntryViewSet, basename='data-entry')
router.register(r'cumulative-data', CumulativeDataViewSet, basename='cumulative-data')
router.register(r'uploads', FileUploadViewSet, basename='upload')

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserViewSet.as_view({'get': 'profile', 'patch': 'profile'}), name='profile'),
    path('', include(router.urls)),
]
