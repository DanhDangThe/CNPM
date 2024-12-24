import json, os
from bookseller import app,db,SMTP_SERVER,SMTP_PORT,SENDER_EMAIL,SENDER_PASSWORD
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import  current_user
from bookseller.models import Category, Product, User, UserRole,ProductDetail,Receipt,ReceiptDetail,DeliveryAddress,Comment,ReceiptUnpaid,ReceiptDetailUnpaid
from sqlalchemy import func
from flask import current_app
from sqlalchemy.sql import extract
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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


def check_login(username,password):
    if username and password :
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        return User.query.filter(User.username.__eq__(username.strip()),User.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)
def load_comments(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id))
def add_comment(content,product_id):

    c=Comment(content=content,product_id=product_id,user=current_user)
    db.session.add(c)
    db.session.commit()
    return c
def get_comment(product_id,page=1):
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size
    end = start + page_size
    return  Comment.query.filter(Comment.product_id.__eq__(product_id))\
                                .order_by(-Comment.id).slice(start, end).all()
def count_comment(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).count()


def add_user(name,username,password,**kwargs):
    password=str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user= User(name=name.strip() ,username=username.strip(),password=password,avatar=kwargs.get('avatar'),email=kwargs.get('email'))
    db.session.add(user)
    db.session.commit()
# def add_address(full_name, phone_number, address, city, state=None, ward=None,
#                 country="Vietnam", is_default=False, user_id=None):
#
#
#     # Tạo đối tượng mới
#     new_address = DeliveryAddress(
#         full_name=full_name,
#         phone_number=phone_number,
#         address=address,
#         city=city,
#         state=state,
#         ward=ward,
#         country=country,
#         is_default=is_default,
#         user_id=user_id
#     )
#
#     # Lưu vào cơ sở dữ liệu
#     db.session.add(new_address)
#     db.session.commit()

def add_address(full_name, phone_number, address, city, state, ward, country, is_default, user_id):
        # Kiểm tra nếu người dùng đã có địa chỉ mặc định
        default_address = DeliveryAddress.query.filter_by(user_id=user_id, is_default=True).first()
        if default_address:
            default_address.is_default = False  # Bỏ trạng thái mặc định của địa chỉ cũ

        # Thêm địa chỉ mới
        new_address = DeliveryAddress(
            full_name=full_name,
            phone_number=phone_number,
            address=address,
            city=city,
            state=state,
            ward=ward,
            country=country,
            is_default=is_default,
            user_id=user_id,
        )
        db.session.add(new_address)
        db.session.commit()  # Lưu thay đổi vào database

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
def add_receipt(cart):
    if cart:

        receipt=Receipt(user_id=current_user.id)
        print("loi")
        db.session.add(receipt)
        for c in cart.values():
            d=ReceiptDetail(receipt=receipt,Product_id=c['id'],quantity=c['quantity'],Unit_price=c['price'])
            db.session.add(d)
        db.session.commit()
def add_receipt_unpaid(cart):
    if cart:
        try:
            # Tạo một đối tượng ReceiptUnpaid
            receiptUnpaid = ReceiptUnpaid(user_id=current_user.id)
            db.session.add(receiptUnpaid)  # Thêm vào session
            db.session.flush()  # Đảm bảo id của receiptUnpaid được tạo trước khi dùng

            # Thêm các sản phẩm vào ReceiptDetailUnpaid
            for c in cart.values():
                # Kiểm tra xem product_id có hợp lệ không
                if 'id' in c and 'quantity' in c and 'price' in c:
                    # Tạo đối tượng ReceiptDetailUnpaid và thêm vào session
                    d = ReceiptDetailUnpaid(
                        receipt_id=receiptUnpaid.id,  # Sử dụng receipt_id
                        Product_id=c['id'],  # Sử dụng Product_id từ cart
                        quantity=c['quantity'],
                        Unit_price=c['price']
                    )
                    db.session.add(d)  # Thêm vào session

            # Commit tất cả các thay đổi vào cơ sở dữ liệu
            db.session.commit()

        except Exception as e:
            db.session.rollback()  # Quay lại nếu có lỗi
            print(f"Error adding receipt: {e}")
def auth_user(username, password):
    password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

    return User.query.filter(User.username.__eq__(username.strip()), User.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def auth_admin(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password), User.user_role.__eq__(UserRole.ADMIN)).first()
def category_stats():
    # return Category.query.join(Product,Product.category_id.__eq__(Category.id))\
    #                                 .add(func.count(Product.id)).group_by(Category.id,Category.name).all()

        return db.session.query(Category.id,Category.name,func.count(Product.id))\
                            .join(Product,Category.id.__eq__(Product.category_id),isouter=True)\
                            .group_by(Category.id,Category.name)

def product_stats(kw=None, from_date=None,to_date=None):
    p=db.session.query(Product.id,Product.name,
                       func.sum(ReceiptDetail.quantity*ReceiptDetail.Unit_price))\
                        .join(ReceiptDetail,ReceiptDetail.Product_id.__eq__(Product.id),isouter=True)\
                        .join(Receipt,Receipt.id.__eq__(ReceiptDetail.receipt_id)) \
                        .group_by(Product.id,Product.name)
    if kw:
        p=p.filter(Product.name.contains(kw))
    # if  from_date:
    #     p=p.filter(Receipt.created_date.__ge__(from_date))
    # if to_date:
    #     p=p.filter(Receipt.created_date.__ge__(from_date))

    return p.all()
def product_month_stats(year):
    return db.session.query(extract('month',Receipt.created_date),
                            func.sum(ReceiptDetail.quantity*ReceiptDetail.Unit_price))\
                            .join(ReceiptDetail,ReceiptDetail.receipt_id.__eq__(Receipt.id))\
                            .filter(extract('year',Receipt.created_date)== year)\
                            .group_by(extract('month',Receipt.created_date))\
                            .order_by(extract('month',Receipt.created_date)).all()

def get_user_addresses(user_id):
    return db.session.query(DeliveryAddress).filter(DeliveryAddress.user_id == user_id).all()
def get_user_email(user_id):
    """
    Truy vấn email của người dùng từ cơ sở dữ liệu.
    """
    print(f"User ID: {user_id}")  # Kiểm tra giá trị user_id
    try:
        user = User.query.filter(User.id == user_id).first()  # Truy vấn người dùng
        print(f"User: {user}")  # Kiểm tra giá trị user

        if user:
            print(f"Email: {user.email}")
            return user.email  # Trả về email của người dùng
        else:
            print("User not found")
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def send_email(to_email, subject, body):
    """
    Hàm gửi email sử dụng SMTP.
    """
    try:
        # Tạo đối tượng MIMEMultipart
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        # Gắn phần nội dung email
        msg.attach(MIMEText(body, 'plain'))

        # Kết nối tới SMTP server và gửi email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Khởi tạo kết nối TLS
            server.login(SENDER_EMAIL, SENDER_PASSWORD)  # Đăng nhập vào email gửi
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())  # Gửi email
        print("Email đã được gửi thành công.")
    except Exception as e:
        print(f"Đã xảy ra lỗi khi gửi email: {e}")


def send_notification_email(user_id, subject, body):
    """
    Hàm gửi thông báo email tới người dùng với thông tin từ cơ sở dữ liệu.
    """

    user_email = get_user_email(user_id)  # Lấy email từ cơ sở dữ liệu
    print("cc")
    if user_email:
        send_email(user_email, subject, body)  # Gửi email nếu tìm thấy email người dùng
    else:
        print(f"Không tìm thấy người dùng với ID: {user_id}")