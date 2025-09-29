from django.core.management.base import BaseCommand
from django.utils import timezone
from books.models import Book, Genre, Order, OrderItem, Customer, SalesStatistics
from django.contrib.auth import get_user_model
from decimal import Decimal
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates test data for sales analytics'

    def handle(self, *args, **kwargs):
        # Create genres if they don't exist
        genres = [
            'Fiction', 'Non-Fiction', 'Science Fiction', 'Mystery', 
            'Romance', 'Biography', 'History', 'Science'
        ]
        genre_objects = []
        for genre_name in genres:
            genre, created = Genre.objects.get_or_create(name=genre_name)
            genre_objects.append(genre)
            if created:
                self.stdout.write(f'Created genre: {genre_name}')

        # Create books if they don't exist
        books = []
        for i in range(20):
            book, created = Book.objects.get_or_create(
                title=f'Test Book {i+1}',
                defaults={
                    'isbn': f'978-3-16-148410-{i}',
                    'price': Decimal(str(random.uniform(10, 50))),
                    'quantity': random.randint(10, 100),
                    'description': f'Description for Test Book {i+1}'
                }
            )
            if created:
                # Add random genres
                book.genres.add(*random.sample(genre_objects, random.randint(1, 3)))
                self.stdout.write(f'Created book: {book.title}')
            books.append(book)

        # Create users and customers if they don't exist
        customers = []
        for i in range(10):
            username = f'test_customer_{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'password': 'testpass123'
                }
            )
            if created:
                self.stdout.write(f'Created user: {username}')

            customer, created = Customer.objects.get_or_create(
                user=user,
                defaults={
                    'phone': f'+37529{random.randint(1000000, 9999999)}',
                    'address': f'Test Address {i}',
                    'birth_date': timezone.now().date() - timedelta(days=random.randint(365*18, 365*70))
                }
            )
            if created:
                self.stdout.write(f'Created customer: {customer.user.username}')
            customers.append(customer)

        # Generate orders and sales statistics for the last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        current_date = start_date
        while current_date <= end_date:
            # Generate 1-5 orders per day
            num_orders = random.randint(1, 5)
            for _ in range(num_orders):
                customer = random.choice(customers)
                order = Order.objects.create(
                    customer=customer,
                    total_amount=Decimal('0.00'),
                    status='completed',
                    created_at=timezone.make_aware(
                        timezone.datetime.combine(current_date, timezone.datetime.min.time())
                    )
                )

                # Add 1-5 items to each order
                num_items = random.randint(1, 5)
                order_items = random.sample(books, num_items)
                for book in order_items:
                    quantity = random.randint(1, 3)
                    price = book.price
                    OrderItem.objects.create(
                        order=order,
                        book=book,
                        quantity=quantity,
                        price=price,
                        total=price * quantity
                    )
                    order.total_amount += price * quantity
                order.save()

            # Calculate sales statistics for the day
            SalesStatistics.calculate_for_date(current_date)
            self.stdout.write(f'Generated data for {current_date}')

            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Successfully generated test data')) 