from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from books.models import Author, Genre, Publisher, Book, Customer, Review
from decimal import Decimal
import random
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with sample book store data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Superuser created.')

        # Create authors
        authors = [
            Author.objects.create(
                name='J.K. Rowling',
                bio='British author best known for the Harry Potter series.'
            ),
            Author.objects.create(
                name='George R.R. Martin',
                bio='American novelist best known for A Song of Ice and Fire series.'
            ),
            Author.objects.create(
                name='Stephen King',
                bio='American author of horror, supernatural fiction, and fantasy.'
            ),
            Author.objects.create(
                name='Agatha Christie',
                bio='British writer known for her detective novels.'
            ),
        ]
        self.stdout.write('Authors created.')

        # Create genres
        genres = [
            Genre.objects.create(name='Fantasy', description='Books involving magic and supernatural phenomena.'),
            Genre.objects.create(name='Science Fiction', description='Books about scientific advancement and future.'),
            Genre.objects.create(name='Mystery', description='Books involving crime solving and detective work.'),
            Genre.objects.create(name='Horror', description='Books intended to frighten and thrill.'),
            Genre.objects.create(name='Romance', description='Books focusing on romantic relationships.'),
        ]
        self.stdout.write('Genres created.')

        # Create publishers
        publishers = [
            Publisher.objects.create(
                name='Penguin Random House',
                website='https://www.penguinrandomhouse.com/'
            ),
            Publisher.objects.create(
                name='HarperCollins',
                website='https://www.harpercollins.com/'
            ),
            Publisher.objects.create(
                name='Simon & Schuster',
                website='https://www.simonandschuster.com/'
            ),
        ]
        self.stdout.write('Publishers created.')

        # Create books
        books = [
            Book.objects.create(
                title='Harry Potter and the Philosopher\'s Stone',
                publisher=publishers[0],
                isbn='9780747532699',
                description='The first book in the Harry Potter series.',
                price=Decimal('29.99'),
                quantity=100,
            ),
            Book.objects.create(
                title='A Game of Thrones',
                publisher=publishers[1],
                isbn='9780553103540',
                description='The first book in A Song of Ice and Fire series.',
                price=Decimal('34.99'),
                quantity=75,
            ),
            Book.objects.create(
                title='The Shining',
                publisher=publishers[2],
                isbn='9780385121675',
                description='A horror novel about a family trapped in a haunted hotel.',
                price=Decimal('24.99'),
                quantity=50,
            ),
            Book.objects.create(
                title='Murder on the Orient Express',
                publisher=publishers[0],
                isbn='9780007119318',
                description='A detective novel featuring Hercule Poirot.',
                price=Decimal('19.99'),
                quantity=60,
            ),
        ]

        # Add authors and genres to books
        books[0].authors.add(authors[0])
        books[0].genres.add(genres[0])
        
        books[1].authors.add(authors[1])
        books[1].genres.add(genres[0])
        
        books[2].authors.add(authors[2])
        books[2].genres.add(genres[3])
        
        books[3].authors.add(authors[3])
        books[3].genres.add(genres[2])
        
        self.stdout.write('Books created.')

        # Create test users and customers
        customers = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='userpass123'
            )
            customer = Customer.objects.create(
                user=user,
                phone=f'+375291234{i:03}',
                address=f'Test Address {i}'
            )
            customers.append(customer)
        self.stdout.write('Users and customers created.')

        # Create reviews (one review per customer per book)
        review_comments = [
            'Great book! Highly recommended.',
            'A masterpiece that keeps you engaged from start to finish.',
            'Excellent storytelling and character development.',
            'One of my favorite books of all time.',
            'A must-read for any book lover.'
        ]
        
        for book in books:
            # Randomly select 3 different customers for each book
            book_reviewers = random.sample(customers, 3)
            for customer in book_reviewers:
                Review.objects.create(
                    book=book,
                    customer=customer,
                    rating=random.randint(3, 5),
                    comment=random.choice(review_comments),
                    is_approved=True
                )
        self.stdout.write('Reviews created.')

        self.stdout.write(self.style.SUCCESS('Successfully populated the database!')) 