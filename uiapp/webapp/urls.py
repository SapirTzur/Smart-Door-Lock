from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_login, name='main'),
    path('user/<int:user_id>/', views.member_account, name='user'),
    
    #path('mymembers/details/<int:id>', views.details, name='details'),
    path('user/<int:user_id>/add_person/',views.add_person, name='add_person'),
    path('user/<int:user_id>/delete_approved/', views.delete_approved, name='delete_approved'),
    path('signup/', views.signup, name='signup'),
    path('notification_alert/<int:user_id>/', views.notification_alert, name = 'notification_alert' ),
]



    
