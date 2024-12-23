import json
import math
from idlelib.query import Query
from itertools import product
from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from sqlalchemy.util import methods_equivalent

from bookseller import app, db, login
from flask_login import login_user,logout_user, login_required
from bookseller.models import UserRole, Product, Category
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

@app.route("/products/<int:products_id>")
def products_detail(products_id):
    products = utils.get_products_by_id(products_id)

    products_detail = utils.get_products_detail_by_id(products_id)



    
    return render_template('products_detail.html', products=products, products_detail=products_detail)

@app.route("/produtcs")
def products():
    cate_id = request.args.get('category_id')
    keyword = request.args.get('keyword')

    page = request.args.get("page", 1)
    page = int(page)
    price_range = request.args.get('price')
    products = utils.load_products(cate_id=cate_id, price_range=price_range, kw=keyword, page=page)
    counter = utils.cout_products()
    return  render_template('products.html', products=products, page=math.ceil(counter / app.config['PAGE_SIZE']))

@app.route("/login",methods=['get','post'])
def user_signin():
    err_msg = ""
    if request.method.__eq__('POST'):

        username= request.form.get('username')
        password=request.form.get('password')

        user=utils.auth_user(username,password)
        depot = utils.auth_depot(username, password)
        seller = utils.auth_seller(username, password)

        if depot:
            login_user(user=depot)
            with open('data/depot.json', 'r', encoding='utf-8') as file:
                depot_data = json.load(file)
            return render_template('depot_manager.html', depot=depot_data)
        elif seller:
            login_user(user=seller)
            return render_template('seller.html')
        elif user:
            login_user(user=user)
            next = request.args.get('next', 'index')
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
                return redirect(url_for('user_signin'))
            else:
                err_msg="Đặt mật khẩu không khớp!!"
        except Exception as ex:
            err_msg="Hệ thống đang có lỗi"+str(ex)

    return render_template('register.html',err_msg=err_msg)



@app.route("/cart")
def cart():
    return render_template('cart.html',stats=utils.count_cart(session.get('cart')))

@app.route("/user_logout")
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))


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

@app.route('/api/update-price', methods=['put'])
def update_price():
    data = request.json
    prod = data.get('product-select')
    quantity = data.get('quantity')



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



@app.route('/admin/login', methods=['post'])
def login_admin():
    username = request.form.get('username')
    password = request.form.get('password')

    admin = utils.auth_admin(username=username, password=password)

    if admin:
        login_user(admin)

    return redirect('/admin')



@app.route("/import_book")
def import_book():
    cates = utils.load_categories()

    return render_template('import_book.html', categories=cates)






@app.route('/logout')
def logout_view():
    logout_user()
    return redirect('/login')


@app.route("/depot_manager")
def depot_manager():
    with open('data/depot.json', 'r', encoding='utf-8') as file:
        depot_data = json.load(file)

    return render_template('depot_manager.html', depot = depot_data)

@app.route("/seller")
def seller():
    return render_template('seller.html')


@app.route('/create_receipt')
def create_receipt():
    prod = Product.query.order_by("id").all()
    return render_template('create_receipt.html', products = prod)

@app.route('/load_receipt')
def load_receipt():
    prod = Product.query.order_by("id").all()
    return render_template('receipt.html', products = prod)


# @app.route('/add_to_depot', methods=['POST'])
# def add_to_depot():
#     if request.method.__eq__('POST'):
#         name = request.form.get('name')
#         category = request.form.get('category')
#         author = request.form.get('author')
#         quantity = request.form.get('quantity')
#         description = request.form.get('description')
#         image = request.form.get('book_img')
#         price = request.form.get('price')
#
#         min_quantity_import = int(app.config['min_quantity'])
#         min_quantity_depot = int(app.config['min_quantity_depot'])
#
#         if int(quantity) < min_quantity_import:
#             err_msg = 'Số luợng nhập không hợp lệ. Vui lòng nhập lại!'
#             return render_template('import_book.html', err_msg=err_msg)
#
#
#         c = Category.query.get(category)
#         p = utils.get_product_by_name(name)
#
#         if not p:
#             p1 = Product(name=name, author=author, quantity=quantity, category_id=c.id, description=description,
#                         image=image, price=price)
#
#             db.session.add(p1)
#             db.session.commit()
#             err_msg = 'Lưu thành công'
#             return render_template('import_book.html', err_msg=err_msg)
#         else:
#             current_quantity = utils.count_books_by_name(name)
#
#             if current_quantity < min_quantity_depot:
#                 p.quantity += int(quantity)
#                 db.session.commit()
#                 err_msg = 'Lưu thành công'
#                 return render_template('import_book.html', err_msg=err_msg)
#             else:
#                 err_msg = 'Số lượng sách tồn đã đủ!!'
#                 return render_template('import_book.html', err_msg=err_msg)

@app.route('/add_to_depot', methods=['POST'])
def add_to_depot():
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        category = request.form.get('category')
        author = request.form.get('author')
        quantity = request.form.get('quantity')
        description = request.form.get('description')
        image = request.form.get('book_img')
        price = request.form.get('price')

        min_quantity_import = int(app.config['min_quantity'])
        min_quantity_depot = app.config['min_quantity_depot']

        if int(quantity) < min_quantity_import:
            err_msg = 'Số luợng nhập không hợp lệ. Vui lòng nhập lại!'
            return render_template('import_book.html', err_msg=err_msg)



        p = utils.get_product_by_name(name)
        c = utils.get_category_by_id(int(category))

        p = {
            "name": name,
            "author": author,
            "quantity": quantity,
            "category": c.name,
            "category_id": category,
            "description": description,
            "image": image,
            "price": price
        }

        file_path = 'data/depot.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            depot_data = json.load(f)

        for p1 in depot_data:
            if p1["name"] == p["name"]:
                if p1["quantity"] < min_quantity_depot:
                    p1["quantity"] += int(quantity)

                    err_msg = 'Lưu thành công'
                    return render_template('import_book.html', err_msg=err_msg)
                else:
                    err_msg = 'Số lượng sách tồn đã đủ!!'
                    return render_template('import_book.html', err_msg=err_msg)

        depot_data.append(p)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(depot_data, f)
        err_msg = 'Lưu thành công'

        return render_template('import_book.html', err_msg=err_msg)

        # if p not in depot_data:
        #     depot_data.append(p)
        #     err_msg = 'Lưu thành công'
        #     return render_template('import_book.html', err_msg=err_msg)
        # else:
        #
        #
        #     if p['quantity'] < min_quantity_depot:
        #         p.quantity += int(quantity)
        #
        #         err_msg = 'Lưu thành công'
        #         return render_template('import_book.html', err_msg=err_msg)
        #     else:
        #         err_msg = 'Số lượng sách tồn đã đủ!!'
        #         return render_template('import_book.html', err_msg=err_msg)




        # if not p:
        #     p1 = Product(name=name, author=author, quantity=quantity, category_id=c.id, description=description,
        #                 image=image, price=price)
        #
        #     db.session.add(p1)
        #     db.session.commit()
        #     err_msg = 'Lưu thành công'
        #     return render_template('import_book.html', err_msg=err_msg)
        # else:
        #     current_quantity = utils.count_books_by_name(name)
        #
        #     if current_quantity < min_quantity_depot:
        #         p.quantity += int(quantity)
        #         db.session.commit()
        #         err_msg = 'Lưu thành công'
        #         return render_template('import_book.html', err_msg=err_msg)
        #     else:
        #         err_msg = 'Số lượng sách tồn đã đủ!!'
        #         return render_template('import_book.html', err_msg=err_msg)


# @app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
# def edit_book(book_id):
#     # Đọc dữ liệu từ file
#     with open('data/depot.json', 'r', encoding='utf-8') as file:
#         depot_data = json.load(file)
#
#     # Tìm sách cần chỉnh sửa
#     book_to_edit = next((book for book in depot_data if book['id'] == book_id), None)
#
#     if request.method == 'POST':
#         # Cập nhật thông tin sách
#         book_to_edit['name'] = request.form['name']
#         book_to_edit['category'] = request.form['category']
#         book_to_edit['author'] = request.form['author']
#         book_to_edit['quantity'] = request.form['quantity']
#         book_to_edit['description'] = request.form['description']
#         book_to_edit['image'] = request.form['image']
#         book_to_edit['price'] = request.form['price']
#
#         # Lưu lại dữ liệu vào file
#         with open('data/depot.json', 'w', encoding='utf-8') as file:
#             json.dump(depot_data, file, ensure_ascii=False, indent=4)
#
#         return redirect(url_for('depot_manager'))
#
#     return render_template('edit_book.html', book=book_to_edit)


@app.route('/create_invoice', methods=['POST'])
def create_invoice():
    data = request.get_json()

    # Dữ liệu hóa đơn
    customer_name = data['customer_name']
    invoice_date = data['invoice_date']
    products = data['products']
    total_price = data['total_price']

    # Tạo ID cho hóa đơn (ví dụ: có thể sử dụng số tự động)
    invoice_id = 1  # Đây là ví dụ, bạn cần logic để sinh ID tự động

    # Lưu hóa đơn vào file hoặc cơ sở dữ liệu (ví dụ: JSON)
    invoice = {
        'id': invoice_id,
        'customer_name': customer_name,
        'invoice_date': invoice_date,
        'products': products,
        'total_price': total_price
    }

    # Lưu vào file JSON (hoặc cơ sở dữ liệu)
    with open('data/invoices.json', 'a', encoding='utf-8') as file:
        json.dump(invoice, file, ensure_ascii=False, indent=4)
        file.write("\n")  # Nếu lưu nhiều hóa đơn, cần phân tách

    return jsonify({"status": "success", "invoice": invoice})







if __name__ == "__main__":
    from bookseller import admin
    app.run(debug=True)
