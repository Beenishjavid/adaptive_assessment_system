from django.urls import path
from . import views

urlpatterns = [
    path('my-results/', views.my_results, name='my_results'),
    path('detail/<int:attempt_id>/', views.result_detail, name='result_detail'),
    path('quiz/<int:quiz_id>/', views.quiz_results, name='quiz_results'),
]
