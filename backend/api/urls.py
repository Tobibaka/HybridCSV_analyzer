from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.api_health, name='api_health'),
    
    # Authentication
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/user/', views.current_user, name='current_user'),
    
    # Dataset operations
    path('datasets/', views.DatasetListView.as_view(), name='dataset_list'),
    path('datasets/<int:pk>/', views.DatasetDetailView.as_view(), name='dataset_detail'),
    path('datasets/<int:pk>/summary/', views.dataset_summary, name='dataset_summary'),
    path('datasets/<int:pk>/records/', views.dataset_records, name='dataset_records'),
    path('datasets/<int:pk>/report/', views.generate_report, name='generate_report'),
    
    # Upload
    path('upload/', views.UploadCSVView.as_view(), name='upload_csv'),
]
