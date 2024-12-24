from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import  Admin
from flask_login import login_manager, LoginManager

import cloudinary
app = Flask(__name__)
app.secret_key = 'asdlajsldjlasjdlajsdlj'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:123456@localhost/bookseller?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE']=8
app.config['COMMENT_SIZE']=5
db=SQLAlchemy(app=app)
cloudinary.config(
    cloud_name= 'dsu2x9kyh',
    api_key= '398425233571762',
    api_secret='6hT1-TYh0LWjsEjudIoAdy1fsxw',
)
login = LoginManager(app=app)
VNP_TMN_CODE = "Z1ZF0D21"  # Mã TmnCode được cung cấp bởi VNPay
VNP_HASH_SECRET = "HULRLIDVD6E5IAIPU3CTR0FMRERSIBE1"  # Khóa bí mật được cung cấp bởi VNPay
VNP_URL = " https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"  # URL Sandbox (thử nghiệm)
RETURN_URL = "https://dbc1-27-75-100-219.ngrok-free.app/payment_return"  # URL khách hàng quay lại sau thanh toán
CALLBACK_URL = "https://dbc1-27-75-100-219.ngrok-free.app/payment_return"  # URL nhận Webhook từ VNPay
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "2251052014danh@ou.edu.vn"  # Thay bằng email của bạn
SENDER_PASSWORD = "040204004884"  # Thay bằng mật khẩu email của bạn

