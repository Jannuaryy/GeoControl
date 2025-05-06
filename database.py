from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime
import bcrypt

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

class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)

# Функция для хеширования пароля
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Пример добавления нового администратора
new_admin = Admin(
    login='admin',
    password=hash_password('123456')
)
#session.add(new_admin)

# Пример добавления нового офиса
new_office = Office(name='МИСИС', location='Somewhere')
#session.add(new_office)

# Пример добавления нового пользователя
new_user = User(phone='123', chat_id='123', name='Katya', avatar='Katya.png')
#session.add(new_user)
session.commit()

# Пример добавления новой локации
new_location = Location(
    id_user=2,
    datetime=datetime(2025, 12, 4, 10, 0),
    location='Somewhere',
    office_distance=200,
    office_name='МИСИС'
)
#session.add(new_location)
session.commit()

session.close()