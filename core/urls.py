from django.urls import path
from .views import (
    RegistrationView,
    LoginView,
    LogoutView,
    ProfileView,
    ContactListView,
    SpamCreateReportView,
    NameSearchView,
    PhoneSearchView,
    UserDetailView,
    ContactCreateView,
    AllSpamNumbersListView,
)
from . import views

urlpatterns = [
       path('register/', RegistrationView.as_view(), name='register'),
       path('login/', LoginView.as_view(), name='login'),
       path('logout/', LogoutView.as_view(), name='logout'),
       path('profile/', ProfileView.as_view(), name='profile'),
       path('contacts/create/', ContactCreateView.as_view(), name='add-contact'),  
       path('contacts/', ContactListView.as_view(), name='list-contacts'),
       path('spam/create/', SpamCreateReportView.as_view(), name='spam-report'),
       path('spam/', AllSpamNumbersListView.as_view(), name='all-spam-numbers'),  
       path('spam/<str:phone_number>/delete/', views.SpamReportDeleteView.as_view(), name='remove-spam'),
       path('spam/<str:phone_number>/', views.SpamNumberDetailView.as_view(), name='spam-number-detail'),
       path('search/name/', NameSearchView.as_view(), name='search-name'),
       path('search/phone/', PhoneSearchView.as_view(), name='search-phone'),
       path('users/<int:id>/', UserDetailView.as_view(), name='user-detail'),
       path('populate-test-data/', views.PopulateTestDataView.as_view(), name='populate-test-data'),
    
]