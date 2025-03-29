from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Contact, SpamReport
from faker import Faker
import random

User = get_user_model()
fake = Faker('en_IN')

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=50, help='Number of users to create')
        parser.add_argument('--contacts-per-user', type=int, default=20, help='Number of contacts per user')
        parser.add_argument('--spam-reports', type=int, default=100, help='Number of spam reports to create')

    def handle(self, *args, **options):
        num_users = options['users']
        contacts_per_user = options['contacts_per_user']
        num_spam_reports = options['spam_reports']

        self.stdout.write(self.style.SUCCESS(f'Creating {num_users} users...'))
        users = []
        all_phone_numbers = set()

        for i in range(num_users):
            username = fake.user_name() + str(i)
            phone_number = fake.phone_number()
            email = fake.email()
            password = 'password123'
            try:
                user = User.objects.create_user(username=username, phone_number=phone_number, email=email, password=password)
                users.append(user)
                all_phone_numbers.add(phone_number)  
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating user {username}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Creating contacts for each user...'))
        
        for user in users:
            for _ in range(contacts_per_user):
                name = fake.name()
                contact_phone = fake.phone_number()
                while contact_phone in all_phone_numbers: 
                    contact_phone = fake.phone_number()
                all_phone_numbers.add(contact_phone)  
                try:
                    Contact.objects.create(user=user, name=name, phone_number=contact_phone)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating contact for {user.username}: {e}'))

        self.stdout.write(self.style.SUCCESS('Sample data population complete.'))
        num_users = options['users']
        contacts_per_user = options['contacts_per_user']
        num_spam_reports = options['spam_reports']

        self.stdout.write(self.style.SUCCESS(f'Creating {num_users} users...'))
        users = []
        all_phone_numbers = set() 

        for i in range(num_users):
            username = fake.user_name() + str(i)
            phone_number = fake.phone_number()
            email = fake.email()
            password = 'password123'
            try:
                user = User.objects.create_user(username=username, phone_number=phone_number, email=email, password=password)
                users.append(user)
                all_phone_numbers.add(phone_number)  
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating user {username}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Creating contacts for each user...'))
                
        for user in users:
            for _ in range(contacts_per_user):
                name = fake.name()
                contact_phone = fake.phone_number()
                while contact_phone in all_phone_numbers:  
                    contact_phone = fake.phone_number()
                all_phone_numbers.add(contact_phone)  
                try:
                    Contact.objects.create(user=user, name=name, phone_number=contact_phone)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating contact for {user.username}: {e}'))

        self.stdout.write(self.style.SUCCESS('Sample data population complete.'))
