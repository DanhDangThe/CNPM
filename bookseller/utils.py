import json, os
from bookseller import app,db
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import  current_user
from bookseller.models import Category, Product, User, UserRole,ProductDetail
from sqlalchemy import func

import hashlib

def read_json(path):
    with open(path,"r") as f:
        return json.load(f)

def get_products_detail_by_id(products_id):
    print(products_id)
    return ProductDetail.query.get(products_id)

def get_products_by_id(products_id):
    return Product.query.get(products_id)

def load_categories():
    return Category.query.order_by("id").all()




def load_products(cate_id=None,price_range=None,kw=None,page=1):
    products = Product.query
    if kw:
        products = products.filter(Product.name.contains(kw))
    if cate_id:
        products = products.filter(Product.category_id == cate_id)
    if price_range:
        if price_range == '1':
            products = products.filter(Product.price >= 0, Product.price <= 15000)
        elif price_range == '2':
            products = products.filter(Product.price > 15000, Product.price <= 30000)
        elif price_range == '3':
            products = products.filter(Product.price > 30000, Product.price <= 50000)
        elif price_range == '4':
            products = products.filter(Product.price > 50000, Product.price <= 70000)
        elif price_range == '5':
            products = products.filter(Product.price > 70000)
    page_size = app.config['PAGE_SIZE']
    start =(page-1)*page_size
    end=start+page_size
    return products.slice(start,end).all()


def cout_products():
    return Product.query.count()


def auth_user(username,password):
    if username and password :
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        return User.query.filter(User.username.__eq__(username.strip()),User.password.__eq__(password)).first()

def auth_admin(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password), User.user_role.__eq__(UserRole.ADMIN)).first()

def auth_depot(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password), User.user_role.__eq__(UserRole.DEPOT_MANAGER)).first()

def auth_seller(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password), User.user_role.__eq__(UserRole.SELLER)).first()

def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_user(name,username,password,**kwargs):
    password=str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user= User(name=name.strip() ,username=username.strip(),password=password,avatar=kwargs.get('avatar'))
    db.session.add(user)
    db.session.commit()


def count_cart(cart):
    total_quantity,total_amount=0,0
    if cart:
        for c in cart.values():
            total_quantity+=c['quantity']
            total_amount+=c['quantity']*c['price']
    return {
        "total_amount":total_amount,
        "total_quantity":total_quantity
    }


def count_books_by_name(product_name):
    # Truy vấn số lượng sản phẩm theo tên
    count = db.session.query(func.sum(Product.quantity)).filter(Product.name == product_name).scalar()
    # Nếu không có sản phẩm, trả về 0
    return count if count else 0


def get_product_by_name(product_name):
    return Product.query.filter_by(name=product_name).first()

def get_category_by_id(id):
    return Category.query.get(id)





