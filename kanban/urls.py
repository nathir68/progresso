from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='kanban/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('', views.boards_list, name='boards_list'),
    path('board/<int:board_id>/', views.board_detail, name='board_detail'),
    
    # AJAX endpoints
    path('api/task/move/', views.move_task, name='move_task'),
    path('api/task/create/', views.create_task, name='create_task'),
    path('api/column/create/', views.create_column, name='create_column'),
]
