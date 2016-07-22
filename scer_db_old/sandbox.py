"""proxied_association.py

same example as basic_association, adding in
usage of :mod:`sqlalchemy.ext.associationproxy` to make explicit references
to ``OrderItem`` optional.


"""

from datetime import datetime

from sqlalchemy import (create_engine, MetaData, Table, Column, Integer,
    String, DateTime, Float, ForeignKey, and_)
from sqlalchemy.orm import mapper, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

# class Order(Base):
#     __tablename__ = 'order'
#
#     order_id = Column(Integer, primary_key=True)
#     customer_name = Column(String(30), nullable=False)
#     order_date = Column(DateTime, nullable=False, default=datetime.now())
#     order_items = relationship("OrderItem", cascade="all, delete-orphan",
#                             backref='order')
#     items = association_proxy("order_items", "item")
#
#     def __init__(self, customer_name):
#         self.customer_name = customer_name
#
# class Item(Base):
#     __tablename__ = 'item'
#     item_id = Column(Integer, primary_key=True)
#     description = Column(String(30), nullable=False)
#     price = Column(Float, nullable=False)
#
#     def __init__(self, description, price):
#         self.description = description
#         self.price = price
#
#     def __repr__(self):
#         return 'Item(%r, %r)' % (
#                     self.description, self.price
#                 )
#
# class OrderItem(Base):
#     __tablename__ = 'orderitem'
#     order_id = Column(Integer, ForeignKey('order.order_id'), primary_key=True)
#     item_id = Column(Integer, ForeignKey('item.item_id'), primary_key=True)
#     price = Column(Float, nullable=False)
#
#     def __init__(self, item, price=None):
#         self.item = item
#         self.price = price or item.price
#     item = relationship(Item, lazy='joined')


class DesignVariable(Base):
    __tablename__ = 'design_variable'
    design_id = Column(Integer, ForeignKey('design.id'), primary_key=True)
    variable_id = Column(Integer, ForeignKey('variable.id'), primary_key=True)
    design = relationship("Design", back_populates="variables")
    variable = relationship("Variable", back_populates="designs")
    dim = Column(Integer)

    def __init__(self, variable, design, dim=1):
        self.variable = variable
        self.design = design
        self.dim = dim

class Design(Base):
    __tablename__ = 'design'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    comments = Column(String(1024), nullable=False)
    variables = relationship("DesignVariable", back_populates="design")

    def __init__(self, name, comments):
        self.name = name
        self.comments = comments


class Variable(Base):
    __tablename__ = 'variable'
    id = Column(Integer, primary_key=True)
    designs = relationship("DesignVariable", back_populates="variable")
    name = Column(String(64), unique=True, nullable=False)
    units = Column(String(64), nullable=False)

    def __init__(self, name, units):
        self.name = name
        self.units = units


if __name__ == '__main__':
    connection_info = dict(user="nirf_lab", pwd="nirf_lab", server="dbserver", db="nirf_lab")
    engine = create_engine("mysql+mysqldb://nirf_lab:nirf_lab@dbserver/nirf_lab" % connection_info, pool_recycle=3600)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session = Session(engine)
    # create variables
    time, salt, temp = Variable('Time', 'minutes'), Variable('KCL', 'molar'), Variable('Temperature', 'degrees celsius')
    session.add_all([time,salt,temp])

    # create a design
    d1 = Design('old-new co-ChIP', 'bla bla bla')

    dv1, dv2 = DesignVariable(time, d1, 1), DesignVariable(salt, d1, 2)

    session.add_all([d1, dv1, dv2])
    session.commit()


    # query the order, print items
    var = session.query(Variable).filter_by(name='Time').one()
    print var.designs
    #
    # # print items based on the OrderItem collection directly
    # print([(assoc.item.description, assoc.price, assoc.item.price)
    #        for assoc in order.order_items])
    #
    # # print items based on the "proxied" items collection
    # print([(item.description, item.price)
    #        for item in order.items])
    #
    # # print customers who bought 'MySQL Crowbar' on sale
    # orders = session.query(Order).\
    #                 join('order_items', 'item').\
    #                 filter(Item.description == 'MySQL Crowbar').\
    #                 filter(Item.price > OrderItem.price)
    # print([o.customer_name for o in orders])