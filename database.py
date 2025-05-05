from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    phone = Column(String)
    chat_id = Column(String)
    name = Column(String)
    avatar = Column(String)

    locations = relationship("Location", back_populates="user")


class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey('users.id'))
    datetime = Column(DateTime)
    location = Column(String)
    office_distance = Column(Integer)
    office_name = Column(String, ForeignKey('offices.name'))

    user = relationship("User", back_populates="locations")
    office = relationship("Office", back_populates="locations")


class Office(Base):
    __tablename__ = 'offices'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    location = Column(String)

    locations = relationship("Location", back_populates="office")


engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Пример добавления нового офиса
new_office = Office(name='МФТИ', location='Somewhere')
session.add(new_office)

# Пример добавления нового пользователя
new_user = User(phone='125', chat_id='125', name='Anya', avatar='Anya.png')
session.add(new_user)
session.commit()

# Пример добавления новой локации
new_location = Location(
    id_user=3,
    datetime=datetime(2025, 5, 15, 9, 0),
    location='Somewhere',
    office_distance=100,
    office_name='МФТИ'
)
session.add(new_location)
session.commit()

session.close()