import math
from itertools import product
from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from bookseller import app, db, login
from flask_login import login_user,logout_user
from bookseller.models import UserRole
import utils
import cloudinary.uploader

@app.route('/')
def index():
    cate_id = request.args.get('category_id')
    keyword = request.args.get('keyword')
    page = request.args.get("page", 1)
    page = int(page)
    products = utils.load_products(cate_id=cate_id, kw=keyword, page=page)
    counter = utils.cout_products()
    return render_template('index.html', products=products, page=math.ceil(counter / app.config['PAGE_SIZE']))


@app.route("/user_login",methods=['get','post'])
def user_singin():
    err_msg = ""
    if request.method.__eq__('POST'):
        user_name= request.form.get('username')
        password=request.form.get('password')
        user=utils.check_login(user_name,password)
        if user:
            login_user(user=user)
            next =request.args.get('next','index')
            return redirect(url_for(next))
        else:
            err_msg="Username hoặc password không chính xác!!"

    return render_template('login.html', err_msg=err_msg)


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route("/register", methods=['get', 'post'])
def user_register():
    err_msg=""
    if request.method.__eq__('POST'):
        name=request.form.get('name')
        username=request.form.get('username')
        password=request.form.get('password')
        email=request.form.get('email')
        confirm=request.form.get('confirm')
        avatar_path=None
        try:
            if password.strip().__eq__(confirm.strip()):
                avatar=request.files.get('avatar')
                if avatar:
                   res = cloudinary.uploader.upload(avatar)
                   avatar_path = res['secure_url']


                utils.add_user(name=name,username=username,password=password,avatar=avatar_path)
                return redirect(url_for('user_singin'))
            else:
                err_msg="Đặt mật khẩu không khớp!!"
        except Exception as ex:
            err_msg="Hệ thống đang có lỗi"+str(ex)

    return render_template('register.html',err_msg=err_msg)


@app.route("/user_logout")
def user_singout():
    logout_user()
    return redirect(url_for('user_singin'))


@app.route('/api/add-cart', methods=['post'])
def add_to_cart():
    data =request.json
    id=str(data.get('id'))
    name=data.get('name')
    price=data.get('price')

    cart= session.get('cart')

    if not cart:
        cart={}
    if id in cart:
        cart[id]['quantity']=cart[id]['quantity']+1
    else:
        cart[id]={
            'id':id,
            'name':name,
            'price':price,
            'quantity':1
        }
    session['cart']=cart
    return jsonify(utils.count_cart(cart))


@app.route('/api/update-cart',methods=['put'])
def update_cart():
    data=request.json
    id=str(data.get('id'))
    quantity=data.get('quantity')
    cart = session.get('cart')
    if cart and id in cart:
        cart[id]['quantity']=quantity
        session['cart'] = cart
    return jsonify(utils.count_cart(cart))


@app.route('/api/delete-cart/<product_id>',methods=['delete'])
def detele_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        del cart[product_id]
        session['cart'] = cart
    return jsonify(utils.count_cart(cart))


@app.context_processor
def common_response():
    return{
        'categories':utils.load_categories(),

        'cart_stats': utils.count_cart(session.get('cart'))
    }


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        u = utils.auth_user(username=username, password=password)
        if u:
            login_user(u)
            return redirect('/')

    return render_template('login.html')


@app.route('/admin/login', methods=['post'])
def login_admin():
    username = request.form.get('username')
    password = request.form.get('password')

    admin = utils.auth_admin(username=username, password=password)
    if admin:
        login_user(admin)

    return redirect('/admin')





@app.route('/logout')
def logout_view():
    logout_user()
    return redirect('/login')






if __name__ == "__main__":
    from bookseller import admin
    app.run(debug=True)
