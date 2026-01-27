from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime , Date,Text
# для определения таблицы и модели
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
#from sqlalchemy.ext.declarative import declarative_base

# для создания отношений между таблицами
from sqlalchemy.orm import relationship, Session

# для настроек
from sqlalchemy import create_engine
from flask_login import UserMixin

# создание экземпляра declarative_base
class Base(DeclarativeBase): pass

class Users(UserMixin,Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)
    name = Column(String(250))
    phone = Column(String(250))
    city = Column(String(250))    
    birth = Column(String(250))
    image = Column(Text)
    created_at =  Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    about = Column(String)
    pets = relationship( "Pets", back_populates="users", cascade="all, delete", passive_deletes=False)
    posts = relationship( "Posts", back_populates="users", cascade="all, delete", passive_deletes=False)
    volonteers = relationship( "Volonteers", back_populates="users", cascade="all, delete", passive_deletes=False)
    profies = relationship( "Profies", back_populates="users", cascade="all, delete", passive_deletes=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        print('')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Pets(Base):
    __tablename__ = 'pets'
    id = Column(Integer, primary_key=True)
    nikname = Column(String(250), nullable=False)
    breed = Column(String(250))
    gender = Column(String(1))
    age = Column(String(250))
    neutered = Column(Boolean)
    about = Column(Text)
    image = Column(Text)
    created_at =  Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    users = relationship("Users", back_populates="pets")

class Posts(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    post = Column(Text)
    image = Column(Text)
    created_at =  Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    users = relationship("Users", back_populates="posts")

class Volonteers(Base):
    __tablename__ = 'volonteers'
    id = Column(Integer, primary_key=True)
    why_i = Column(Text)
    i_can = Column(Text)
    created_at =  Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    users = relationship("Users", back_populates="volonteers")

class Profies(Base):
    __tablename__ = 'profies'
    id = Column(Integer, primary_key=True)
    why_i = Column(Text)
    i_can = Column(Text)
    created_at =  Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    users = relationship("Users", back_populates="profies")
    image = Column(Text)

class Chat(Base):
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    id_from = Column(Integer)
    id_to = Column(Integer)
    message = Column(Text)
    created_at =  Column(DateTime, default=func.now())
    delivered_at = Column(DateTime)

# class Images(Base):
#     __tablename__ = 'images'
#     id = Column(Integer, primary_key=True)
#     why_i = Column(Text)
#     i_can = Column(Text)
#     created_at =  Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
#     users = relationship("Users", back_populates="profies")

# создает экземпляр create_engine в конце файла
#engine = create_engine('sqlite:///database.db')
print('success maybe')
#Base.metadata.create_all(engine)