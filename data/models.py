import _io

from sqlalchemy import *
from sqlalchemy.orm import mapped_column, relationship, Mapped, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_serializer import SerializerMixin
import os

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from data.db_session import SqlAlchemyBase, create_session


# Base = declarative_base()


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    name = Column(String, unique=True)
    hashed_password = Column(String)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Item(SqlAlchemyBase):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    type = Column(Integer)
    status = Column(Boolean)

    def get_props(self):
        session = create_session()
        fancy_props = []
        for description in session.query(Description).filter(Description.item == self.id):
            prop_value = session.query(PropValue).filter_by(id=description.value).first()
            if prop_value:
                fancy_props.append(prop_value.value)
        return fancy_props

    def set_image(self, file: bytes):
        with open(f'db/images/{self.id}.png', 'wb') as f:
            f.write(file)

    def add_prop(self, prop_id):
        session = create_session()
        description = Description()
        description.item = self.id
        description.value = session.query(PropValue).filter(PropValue.id == prop_id).first().id
        session.add(description)
        session.commit()


class Property(SqlAlchemyBase):
    __tablename__ = "prop_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class Description(SqlAlchemyBase):
    __tablename__ = "descriptions"

    id = Column(Integer, primary_key=True, index=True)
    item = Column(Integer, ForeignKey('items.id'))
    value = Column(String, ForeignKey('prop_values.id'))


class PropValue(SqlAlchemyBase):
    __tablename__ = "prop_values"

    id = Column(Integer, primary_key=True)
    type = Column(Integer, ForeignKey('prop_types.id'))
    value = Column(String)