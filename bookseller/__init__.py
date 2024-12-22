from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import  Admin
from flask_login import login_manager, LoginManager

import cloudinary
app = Flask(__name__)
app.secret_key = 'asdlajsldjlasjdlajsdlj'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:Admin123@localhost/bookseller?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE']=8
app.config['min_quantity']=150
app.config['min_quantity_depot']=300
app.config['order_cancel_time']=48
db=SQLAlchemy(app=app)
cloudinary.config(
    cloud_name= 'dsu2x9kyh',
    api_key= '398425233571762',
    api_secret='6hT1-TYh0LWjsEjudIoAdy1fsxw',
)
login = LoginManager(app=app)

