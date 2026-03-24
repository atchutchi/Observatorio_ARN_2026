from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('indicator/<str:category_code>/', views.DashboardIndicatorView.as_view(), name='dashboard-indicator'),
    path('market-share/', views.DashboardMarketShareView.as_view(), name='dashboard-market-share'),
    path('trends/', views.DashboardTrendsView.as_view(), name='dashboard-trends'),
    path('comparative/', views.DashboardComparativeView.as_view(), name='dashboard-comparative'),
    path('hhi/', views.DashboardHHIView.as_view(), name='dashboard-hhi'),
    path('export/', views.DashboardExportView.as_view(), name='dashboard-export'),
]
