from rest_framework import generics, permissions, status, views, response
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Count, Q
from .models import Contact, SpamReport, User
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ContactSerializer,
    SpamReportSerializer,
    SearchResultSerializer,
    UserDetailSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.db import models
from django.core.management import call_command
from django.conf import settings
from django.shortcuts import get_object_or_404

User = get_user_model()

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(phone_number=serializer.validated_data['phone_number'], password=serializer.validated_data['password'])
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class ContactListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactSerializer

    def get_queryset(self):
        return self.request.user.contacts.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SpamCreateReportView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SpamReportSerializer

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

class NameSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchResultSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        if query:
            registered_users = User.objects.annotate(
                spam_count=Count('spamreport', filter=Q(spamreport__phone_number=models.F('phone_number')))
            ).filter(Q(username__istartswith=query) | Q(username__icontains=query)).distinct()

            contacts = Contact.objects.filter(
                Q(name__istartswith=query) | Q(name__icontains=query),
                user__in=User.objects.all()  
            ).exclude(phone_number__in=registered_users.values_list('phone_number', flat=True)).distinct()

            results = []
            for user in registered_users.order_by('username'):
                spam_reports = SpamReport.objects.filter(phone_number=user.phone_number).count()
                total_reports = SpamReport.objects.count()
                spam_likelihood = (spam_reports / total_reports) * 100 if total_reports > 0 else 0
                results.append({'name': user.username, 'phone_number': user.phone_number, 'spam_likelihood': spam_likelihood})

            for contact in contacts.order_by('name'):
                spam_reports = SpamReport.objects.filter(phone_number=contact.phone_number).count()
                total_reports = SpamReport.objects.count()
                spam_likelihood = (spam_reports / total_reports) * 100 if total_reports > 0 else 0
                results.append({'name': contact.name, 'phone_number': contact.phone_number, 'spam_likelihood': spam_likelihood})

            return results
        return []
    
class SpamNumberDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, phone_number):
        is_spam = SpamReport.objects.filter(phone_number=phone_number).exists()
        report_count = SpamReport.objects.filter(phone_number=phone_number).count()
        return response.Response({
            'phone_number': phone_number,
            'is_spam': is_spam,
            'report_count': report_count
        })

class PhoneSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchResultSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        if query:
            registered_user = User.objects.annotate(
                spam_count=Count('spamreport', filter=Q(spamreport__phone_number=models.F('phone_number')))
            ).filter(phone_number=query).first()

            if registered_user:
                spam_reports = SpamReport.objects.filter(phone_number=registered_user.phone_number).count()
                total_reports = SpamReport.objects.count()  
                spam_likelihood = (spam_reports / total_reports) * 100 if total_reports > 0 else 0
                return [{'name': registered_user.username, 'phone_number': registered_user.phone_number, 'spam_likelihood': spam_likelihood}]
            else:
                contacts = Contact.objects.filter(phone_number=query, user__in=User.objects.all()).distinct()
                results = []
                for contact in contacts:
                    spam_reports = SpamReport.objects.filter(phone_number=contact.phone_number).count()
                    total_reports = SpamReport.objects.count()
                    spam_likelihood = (spam_reports / total_reports) * 100 if total_reports > 0 else 0
                    results.append({'name': contact.name, 'phone_number': contact.phone_number, 'spam_likelihood': spam_likelihood})
                return results
        return []

class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer
    queryset = User.objects.all()
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        spam_reports = SpamReport.objects.filter(phone_number=instance.phone_number).count()
        total_reports = SpamReport.objects.count() 
        spam_likelihood = (spam_reports / total_reports) * 100 if total_reports > 0 else 0

        is_contact = Contact.objects.filter(user=request.user, phone_number=instance.phone_number).exists()

        serializer = self.get_serializer(instance)
        data = serializer.data
        data['spam_likelihood'] = spam_likelihood
        if not is_contact:
            data.pop('email', None)
        return Response(data)
    
class SpamLikelihoodView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, phone_number):
        total_reporting_users = User.objects.count()
        spam_reports_count = SpamReport.objects.filter(phone_number=phone_number).count()

        if total_reporting_users > 0:
            likelihood_percentage = (spam_reports_count / total_reporting_users) * 100
            return response.Response({'phone_number': phone_number, 'spam_likelihood': f'{likelihood_percentage:.2f}%'})
        else:
            return response.Response({'phone_number': phone_number, 'spam_likelihood': '0.00% (No users to report)'})
        
class ContactCreateView(generics.CreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ContactListView(generics.ListAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)

class PopulateTestDataView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]   

    def post(self, request):
        if settings.DEBUG:
            try:
                call_command('populate_data') 
                return response.Response({'message': 'Test data population initiated successfully.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return response.Response({'error': f'Error during data population: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return response.Response({'error': 'This endpoint is only available in DEBUG mode.'}, status=status.HTTP_403_FORBIDDEN)
        
class ContactDeleteView(generics.DestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'  

    def get_queryset(self):
        """Ensure a user can only delete their own contacts."""
        return Contact.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return response.Response({'message': 'Deleted successfully.'}, status=status.HTTP_200_OK)
        except Contact.DoesNotExist:
            return response.Response({'error': 'Contact not found.'}, status=status.HTTP_404_NOT_FOUND)
        
class SpamReportDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'phone_number'
    lookup_url_kwarg = 'phone_number'

    def get_queryset(self):
        """Ensure a user can only remove their own spam reports."""
        return SpamReport.objects.filter(reported_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            phone_number = self.kwargs.get('phone_number')
            instance = get_object_or_404(queryset, phone_number=phone_number)
            self.perform_destroy(instance)
            return response.Response({'message': 'Spam report removed successfully.'}, status=status.HTTP_200_OK)
        except SpamReport.DoesNotExist:
            return Response({'error': 'You have not reported this number as spam.'}, status=status.HTTP_404_NOT_FOUND)

class AllSpamNumbersListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SpamReportSerializer 

    def get_queryset(self):
        """Return a queryset of unique spam phone numbers."""
        return SpamReport.objects.values('phone_number').distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        results = [{'phone_number': item['phone_number']} for item in queryset]
        return Response(results)
