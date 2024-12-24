import random
from unittest.mock import DEFAULT

from jinja2.async_utils import auto_aiter
from sqlalchemy.orm import relationship, Relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Boolean,DateTime
from sqlalchemy.sql import func


from datetime import datetime
from bookseller import db, app
from enum import Enum as UserEnum
import hashlib
from flask_login import UserMixin
class UserRole(UserEnum):
    ADMIN=1
    USER=2

class BaseModel(db.Model):
    __abstract__=True
    id =Column(Integer,primary_key=True,autoincrement=True)
class Category(BaseModel):

    name = Column(String(50), nullable=False, unique=True)
    products=relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    price = Column(Float, default=0)
    image = Column(String(100), nullable=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    detail = relationship('ProductDetail', backref='product', uselist=False)
    receipt_details = relationship('ReceiptDetail', backref='product', lazy=True)
    comments = Relationship('Comment', backref='product', lazy=True)
    receipt_details_Unpaid = relationship('ReceiptDetailUnpaid', backref='product', lazy=True)

    def __str__(self):
        return self.name
class ProductDetail(BaseModel):
    SupplierName=Column(String(50),nullable=False)
    author=Column(String(50),nullable=False)
    publishing_house=Column(String(50),nullable=False)
    year=Column(Integer,nullable=False)
    language=Column(String(50),nullable=False,)
    weight=Column(Integer,nullable=False)
    packaging_size=Column(String(50),nullable=False)
    number_of_pages=Column(String(50),nullable=False)
    form=Column(String(50),nullable=False,unique=True)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)



class User(db.Model,UserMixin):
    id=Column(Integer,primary_key=True, autoincrement=True)
    name=Column(String(250),nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password =Column(String(100),nullable=False)
    avatar=Column(String(100))
    active=Column(Boolean, default=True)
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    joined_date=Column(DateTime, default=datetime.now())
    email = Column(String(100))
    receipts = relationship('Receipt', backref='user', lazy=True)
    comment = relationship('Comment', backref='user', lazy=True)
    receiptsUnpaid = relationship('ReceiptUnpaid', backref='user', lazy=True)



class Receipt(BaseModel):
    created_date=Column(DateTime,default=datetime.now())
    user_id=Column(Integer,ForeignKey(User.id),nullable=False)
    details= relationship('ReceiptDetail',backref='receipt',lazy=True)
class ReceiptUnpaid(BaseModel):
    created_date=Column(DateTime,default=datetime.now())
    user_id=Column(Integer,ForeignKey(User.id),nullable=False)
    details = relationship('ReceiptDetailUnpaid', backref='receipt1', lazy=True)

class ReceiptDetail(db.Model):
    receipt_id=Column(Integer,ForeignKey(Receipt.id),nullable=False,primary_key=True)
    Product_id=Column(Integer,ForeignKey(Product.id),nullable=False,primary_key=True)
    quantity=Column(Integer,default=0)
    Unit_price=Column(Float,default=0)

class ReceiptDetailUnpaid(db.Model):
    receipt_id=Column(Integer,ForeignKey(ReceiptUnpaid.id),nullable=False,primary_key=True)
    Product_id=Column(Integer,ForeignKey(Product.id),nullable=False,primary_key=True)
    quantity=Column(Integer,default=0)
    Unit_price=Column(Float,default=0)


class Comment(BaseModel):
    content=Column(String(255),nullable=False)
    product_id=Column(Integer,ForeignKey(Product.id),nullable=False)
    user_id=Column(Integer,ForeignKey(User.id),nullable=False)
    created_date=Column(DateTime,default=func.now())
    def __str__(self):
        return self.content


class DeliveryAddress(BaseModel):
    full_name = Column(String(100), nullable=False)  # Tên người nhận
    phone_number = Column(String(15), nullable=False)  # Số điện thoại liên hệ
    address = Column(String(255), nullable=False)  # Địa chỉ cụ thể
    city = Column(String(50), nullable=False)  # Thành phố
    state = Column(String(50), nullable=True)  # Tỉnh/Bang (nếu có)
    ward=Column(String(50), nullable=True)
    country = Column(String(50), nullable=False, default="Vietnam")  # Quốc gia, mặc định là Việt Nam
    is_default = Column(Boolean, default=False)  # Đánh dấu địa chỉ mặc định
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # Liên kết với bảng User
    user = relationship('User', backref='delivery_addresses', lazy=True)
    def __str__(self):
        return f"{self.full_name}, {self.address}, {self.city}, {self.country}"


if __name__ == '__main__':

    with app.app_context():
        # d2 = ProductDetail(
        #     SupplierName='Kim Đồng1',
        #     author='Yoshito Usui, Takata Mirei1',
        #     publishing_house='Kim Đồng1',
        #     year='20241',
        #     language='Tiếng Việt1',
        #     weight='1801',
        #     packaging_size='18 x 13 x 0.8 cm1',
        #     number_of_pages='1661',
        #     form='Bìa Mềm1',
        #     product_id='1')
        # db.session.add_all([d2])
    # cd1 = Category(name='Sách Học')
    # c1 = Category(name='Tiểu Thuyết')
    # c1 = Category(name='Truyên Tranh')
    #     c1 = Category(name='Truyện ngắn - Tản Văn')
    #     c2 = Category(name='Tác Phẩm Kinh Điển')
    #     c3 = Category(name='Huyền Bí - Giả Tưởng - Kinh Dị')
    #     c4 = Category(name='Ngôn Tình')
    #     c5 = Category(name='Light Novel')
    #     db.session.add_all([c1, c2, c3,c4,c5])
        db.session.commit()
    #     Data=[{
    #          "id": 1,
    #          "name": "Tôi thích dáng  vẻ Nỗ Lực Của Chính Mình",
    #          "description": "Abc,xbz",
    #          "price": 99000,
    #          "image": "images/ve-dep-cua-toi.png",
    #          "category_id": 2
    #         }, {
    #          "id": 2,
    #          "name": "shin Câu Bé Bút Chì Tập 20",
    #          "description": "chua co mo ta",
    #          "price": 200000,
    #          "image": "images/shin-cau-be-but-chi.png",
    #          "category_id": 1
    #         }, {
    #          "id": 3,
    #          "name": "Thuật Thao Túng",
    #         "description": "chua co mo ta lam sau",
    #          "price": 132000,
    #          "image": "images/thuat-thao-tung.png",
    #          "category_id": 2
    #         }, {
    #          "id": 4,
    #          "name": "Dragonball",
    #         "description": "chua co mo ta lam sau",
    #          "price": 32000,
    #          "image": "images/Dragonball.png",
    #          "category_id": 1
    #         }, {
    #          "id": 5,
    #          "name": "Thám Tử Lừng Danh Conan Tập 8",
    #         "description": "chua co mo ta lam sau",
    #          "price": 56000,
    #          "image": "images/tham-tu-lung-danh-conan-tap8.png",
    #          "category_id": 1
    #         }, {
    #          "id": 6,
    #          "name": "Thời Thơ Ấu",
    #         "description": "chua co mo ta lam sau",
    #          "price": 78000,
    #          "image": "images/thoi-tho-au-song-ngu.png",
    #          "category_id": 2
    #         }, {
    #          "id": 7,
    #          "name": "Những Tấm Lòng Cao Cả",
    #         "description": "chua co mo ta lam sau",
    #          "price": 78000,
    #          "image": "images/nhung-tam-long-cao-ca.png",
    #          "category_id": 2
    #         }, {
    #          "id": 8,
    #          "name": "Hiểu Bộ não lý giải ứng sử",
    #         "description": "chua co mo ta lam sau",
    #          "price": 78000,
    #          "image": "images/hieu-bo-nao-ly-giai-ung-su.png",
    #          "category_id": 2
    #         }, {
    #          "id": 9,
    #          "name": "Dune Mti",
    #         "description": "chua co mo ta lam sau",
    #          "price": 78000,
    #          "image": "images/Dune-mti.png",
    #          "category_id": 2
    #         }
    #     ]
    #     for p in Data:
    #         pro= Product(name=p['name'], price=p['price'], image=p['image'], description=p['description'], category_id=p['category_id'])
    #         db.session.add(pro)
        db.create_all()
        db.session.commit()
    #     # u = User(name='admin', username='admin', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
        #          user_role=UserRole.ADMIN)
        # db.session.add(u)
        # db.session.commit()


