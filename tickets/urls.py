from django.urls import path
from django.views.generic import RedirectView
from .views import WelcomeView, Menu, ServicePage, OperatorMenu, Next

urlpatterns = [
    path('welcome/', WelcomeView.as_view()),
    path('menu/', Menu.as_view()),
    path('get_ticket/<slug:page>', ServicePage.as_view()),
    path('processing', OperatorMenu.as_view()),
    path('processing/', RedirectView.as_view(url='/processing')),
    path('next', Next.as_view())
]
