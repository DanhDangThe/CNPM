import random
from unittest.mock import DEFAULT

from jinja2.async_utils import auto_aiter
from sqlalchemy.orm import relationship, Relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Boolean,DateTime
from unicodedata import category
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

if __name__ == '__main__':

    with app.app_context():
        d2 = ProductDetail(
            SupplierName='Kim Đồng1',
            author='Yoshito Usui, Takata Mirei1',
            publishing_house='Kim Đồng1',
            year='20241',
            language='Tiếng Việt1',
            weight='1801',
            packaging_size='18 x 13 x 0.8 cm1',
            number_of_pages='1661',
            form='Bìa Mềm1',
            product_id='1')
        db.session.add_all([d2])
    # cd1 = Category(name='Sách Học')
    # c1 = Category(name='Tiểu Thuyết')
    # c1 = Category(name='Truyên Tranh')
    # c1 = Category(name='Truyện ngắn - Tản Văn')
    # c2 = Category(name='Tác Phẩm Kinh Điển')
    # c3 = Category(name='Huyền Bí - Giả Tưởng - Kinh Dị')
    # c4 = Category(name='Ngôn Tình')
    # c5 = Category(name='Light Novel')
    # db.session.add_all([c1, c2, c3,c4,c5])
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
    #     db.session.commit()
    #     # u = User(name='admin', username='admin', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
        #          user_role=UserRole.ADMIN)
        # db.session.add(u)
        db.session.commit()


