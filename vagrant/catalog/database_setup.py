from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(250))


class Region(Base):
    __tablename__ = 'region'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easy serializable format"""
        return{
            'name': self.name,
            'id': self.id,
        }


class Wine(Base):
    __tablename__ = 'wine'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250), nullable=False)
    price = Column(String(8))
    region_id = Column(Integer, ForeignKey('region.id'))
    region = relationship(Region)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easy serializable format"""
        return{
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'price': self.price,

        }


engine = create_engine('sqlite:///winecatalog.db')
Base.metadata.create_all(engine)
