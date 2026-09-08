"""
sqlalchemy_schemadisplay との比較用モデル定義。

normalization_demo.py の 3NF（正規化完了形）と同じ「受注管理」スキーマを
SQLAlchemy の宣言的モデルとして定義する。
  顧客 (1) --- (N) 受注 (1) --- (N) 受注明細 (N) --- (1) 商品
  担当者 (1) --- (N) 受注
"""

from __future__ import annotations

from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Customer(Base):
    __tablename__ = "顧客"

    顧客CD = Column(String(10), primary_key=True)
    顧客名 = Column(String(50), nullable=False)
    顧客住所 = Column(String(100))

    orders = relationship("Order", back_populates="customer")


class Staff(Base):
    __tablename__ = "担当者"

    担当者CD = Column(String(10), primary_key=True)
    担当者名 = Column(String(50), nullable=False)

    orders = relationship("Order", back_populates="staff")


class Product(Base):
    __tablename__ = "商品"

    商品CD = Column(String(10), primary_key=True)
    商品名 = Column(String(50), nullable=False)
    単価 = Column(Integer, nullable=False)

    details = relationship("OrderDetail", back_populates="product")


class Order(Base):
    __tablename__ = "受注"

    受注No = Column(String(10), primary_key=True)
    受注日 = Column(Date, nullable=False)
    顧客CD = Column(String(10), ForeignKey("顧客.顧客CD"), nullable=False)
    担当者CD = Column(String(10), ForeignKey("担当者.担当者CD"), nullable=False)

    customer = relationship("Customer", back_populates="orders")
    staff = relationship("Staff", back_populates="orders")
    details = relationship("OrderDetail", back_populates="order")


class OrderDetail(Base):
    __tablename__ = "受注明細"

    受注No = Column(String(10), ForeignKey("受注.受注No"), primary_key=True)
    商品CD = Column(String(10), ForeignKey("商品.商品CD"), primary_key=True)
    数量 = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="details")
    product = relationship("Product", back_populates="details")
