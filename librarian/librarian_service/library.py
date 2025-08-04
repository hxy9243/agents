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

    def search_books(self, query: str) -> List[Book]:
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
