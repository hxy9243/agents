from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import date

# Custom Exceptions

class BookNotFound(Exception):
    pass

class CopyNotFound(Exception):
    pass

class MemberNotFound(Exception):
    pass

class LoanNotFound(Exception):
    pass

class CopyAlreadyBorrowed(Exception):
    pass

# Data Models

class Book(BaseModel):
    book_id: str  # ISBN or other unique identifier
    title: str
    author: str

class BookCopy(BaseModel):
    copy_id: int
    book_id: str
    status: str = "Available"  # Available, Borrowed, Lost

class Member(BaseModel):
    member_id: int
    name: str
    email: str

class Loan(BaseModel):
    loan_id: int
    copy_id: int
    member_id: int
    loan_date: date
    due_date: date
    return_date: Optional[date] = None

# Library In-Memory Database

class Library:
    def __init__(self):
        self.books: Dict[str, Book] = {}
        self.book_copies: Dict[int, BookCopy] = {}
        self.members: Dict[int, Member] = {}
        self.loans: Dict[int, Loan] = {}
        self._next_copy_id = 1
        self._next_member_id = 1
        self._next_loan_id = 1

    def add_book(self, book_id: str, title: str, author: str, num_copies: int = 1):
        if book_id not in self.books:
            self.books[book_id] = Book(book_id=book_id, title=title, author=author)

        for _ in range(num_copies):
            copy_id = self._next_copy_id
            self.book_copies[copy_id] = BookCopy(copy_id=copy_id, book_id=book_id)
            self._next_copy_id += 1

    def add_member(self, name: str, email: str) -> Member:
        member_id = self._next_member_id
        member = Member(member_id=member_id, name=name, email=email)
        self.members[member_id] = member
        self._next_member_id += 1
        return member

    def search_member(self, name: str) -> Member:
        for member in self.members:
            if name.lower() in member.name.lower():
                return member

        raise MemberNotFound

    def borrow_book(self, book_id: str, member_id: int) -> Loan:
        if member_id not in self.members:
            raise MemberNotFound(f"Member with id {member_id} not found.")

        available_copies = [
            copy for copy in self.book_copies.values()
            if copy.book_id == book_id and copy.status == "Available"
        ]

        if not available_copies:
            raise CopyNotFound(f"No available copies of book with id {book_id}.")

        copy_to_loan = available_copies[0]
        copy_to_loan.status = "Borrowed"

        loan_id = self._next_loan_id
        loan_date = date.today()
        due_date = date.fromordinal(loan_date.toordinal() + 14) # 2 weeks loan
        loan = Loan(
            loan_id=loan_id,
            copy_id=copy_to_loan.copy_id,
            member_id=member_id,
            loan_date=loan_date,
            due_date=due_date
        )
        self.loans[loan_id] = loan
        self._next_loan_id += 1
        return loan

    def return_book(self, copy_id: int) -> Loan:
        if copy_id not in self.book_copies:
            raise CopyNotFound(f"Book copy with id {copy_id} not found.")

        loan = next((l for l in self.loans.values() if l.copy_id == copy_id and l.return_date is None), None)

        if not loan:
            raise LoanNotFound(f"No active loan found for copy id {copy_id}.")

        self.book_copies[copy_id].status = "Available"
        loan.return_date = date.today()
        return loan

    def search_books(self, query: str) -> list[Book]:
        if query == "":
            return [book for book in self.books.values()]

        return [
            book for book in self.books.values()
            if query.lower() in book.title.lower() or query.lower() in book.author.lower()
        ]

    def get_member_loans(self, member_id: int) -> List[Loan]:
        if member_id not in self.members:
            raise MemberNotFound(f"Member with id {member_id} not found.")
        return [loan for loan in self.loans.values() if loan.member_id == member_id]


def add_example_data(library: Library):
    library.add_book(
        "978-0345391803", "The Hitchhiker's Guide to the Galaxy", "Douglas Adams", 3
    )
    library.add_book("978-0618640157", "The Lord of the Rings", "J.R.R. Tolkien", 2)
    library.add_book("978-0743273565", "The Da Vinci Code", "Dan Brown", 5)
    library.add_book("978-0439023528", "The Hunger Games", "Suzanne Collins", 4)
    library.add_book("978-0385537858", "The Martian", "Andy Weir", 3)
    library.add_book("978-1451673319", "Fahrenheit 451", "Ray Bradbury", 2)
    library.add_book("978-0743273565", "To Kill a Mockingbird", "Harper Lee", 4)
    library.add_book("978-0452284234", "1984", "George Orwell", 3)
    library.add_book("978-0743273565", "The Great Gatsby", "F. Scott Fitzgerald", 2)
    library.add_book("978-0142437230", "The Catcher in the Rye", "J.D. Salinger", 1)
    library.add_book(
        "978-0307474278", "The Girl with the Dragon Tattoo", "Stieg Larsson", 3
    )
    library.add_book("978-0316067938", "The Road", "Cormac McCarthy", 2)
    library.add_book("978-0743273565", "Brave New World", "Aldous Huxley", 2)
    library.add_book("978-0446310789", "To Kill a Mockingbird", "Harper Lee", 3)
    library.add_book("978-0679783268", "Pride and Prejudice", "Jane Austen", 4)
    library.add_book("978-0061120084", "The Alchemist", "Paulo Coelho", 5)
    library.add_book("978-0307277671", "The Kite Runner", "Khaled Hosseini", 3)
    library.add_book("978-1400033423", "The Secret History", "Donna Tartt", 2)
    library.add_book("978-0307387899", "Gone Girl", "Gillian Flynn", 4)
    library.add_book("978-0553380033", "A Brief History of Time", "Stephen Hawking", 2)

    library.add_member("Alice", "alice@example.com")
    library.add_member("Bob", "bob@example.com")
    library.add_member("Charlie", "charlie@example.com")
    library.add_member("Diana", "diana@example.com")
    library.add_member("Eve", "eve@example.com")
