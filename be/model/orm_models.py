from sqlalchemy import text, Index, Column, Integer, Text, LargeBinary, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TSVECTOR


Base = declarative_base()
"""
def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return func.to_tsvector('english', text(s))
"""
class Book(Base):
    __tablename__ = 'bookstore_book'

    id = Column(Text, primary_key=True)
    title = Column(Text)
    author = Column(Text)
    publisher = Column(Text)
    original_title = Column(Text)
    translator = Column(Text)
    pub_year = Column(Text)
    pages = Column(Integer)
    price = Column(Integer)
    currency_unit = Column(Text)
    binding = Column(Text)
    isbn = Column(Text)
    author_intro = Column(Text)
    book_intro = Column(Text)
    content = Column(Text)
    tags = Column(Text)
    picture = Column(LargeBinary)
    token = Column(TSVECTOR)
"""
    __table_args__ = (
        Index(
            'ix_book_tsv',
            to_tsvector_ix('title', 'author', 'tags', 'book_intro', 'content'),
            postgresql_using='gin'
        ),
    )
"""
class NewOrder(Base):
    __tablename__ = 'bookstore_new_order'

    order_id = Column(Text, primary_key=True)
    user_id = Column(Text)
    store_id = Column(Text)
    status = Column(Text)
    time = Column(DateTime)


class NewOrderDetail(Base):
    __tablename__ = 'bookstore_new_order_detail'

    order_id = Column(Text, primary_key=True)
    book_id = Column(Text, primary_key=True)
    count = Column(Integer)
    price = Column(Integer)


class Store(Base):
    __tablename__ = 'bookstore_store'

    store_id = Column(Text, primary_key=True)
    book_id = Column(Text, primary_key=True)
    book_info = Column(Text)
    stock_level = Column(Integer)


class User(Base):
    __tablename__ = 'bookstore_user'

    password = Column(Text, nullable=False)
    balance = Column(Integer, nullable=False)
    user_id = Column(Text, primary_key=True)
    token = Column(Text)
    terminal = Column(Text)


class UserStore(Base):
    __tablename__ = 'bookstore_user_store'

    user_id = Column(Text, primary_key=True)
    store_id = Column(Text, primary_key=True)

def createTable(engine):
    Base.metadata.create_all(engine)



