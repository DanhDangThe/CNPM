import json, os
from bookseller import app,db
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import  current_user
from bookseller.models import Category, Product, User, UserRole

import hashlib

def read_json(path):
    with open(path,"r") as f:
        return json.load(f)


def load_categories():
    return Category.query.order_by("id").all()


def load_products(cate_id=None,kw=None,from_price=None,to_price=None,page=1):
    products = Product.query
    if kw:
        products = products.filter(Product.name.contains(kw))
    if cate_id:
        products = products.filter(Product.category_id == cate_id)
    page_size = app.config['PAGE_SIZE']
    start =(page-1)*page_size
    end=start+page_size
    return products.slice(start,end).all()


def cout_products():
    return Product.query.count()


def check_login(username,password):
    if username and password :
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        return User.query.filter(User.username.__eq__(username.strip()),User.password.__eq__(password)).first()


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


def auth_user(username, password):
    password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

    return User.query.filter(User.username.__eq__(username.strip()), User.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def auth_admin(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password), User.user_role.__eq__(UserRole.ADMIN)).first()