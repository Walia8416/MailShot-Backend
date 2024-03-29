from django.urls import path
from gmail import views

urlpatterns = [
    path('emails/', views.InboxView.as_view()),
    path('emails/<str:pk>/', views.detailEmailView),
    path('summarize/<str:pk>/',views.summarizeEmailView),
]