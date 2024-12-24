import math
from ctypes import util
from itertools import product
from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from bookseller import app, db, login, VNP_TMN_CODE, VNP_HASH_SECRET, VNP_URL, RETURN_URL, CALLBACK_URL
from bookseller.models import DeliveryAddress
from flask_login import login_user,logout_user,login_required
from bookseller.models import UserRole, Comment
import utils
import cloudinary.uploader
from flask_login import current_user
import hashlib
from urllib.parse import urlencode
import datetime
import urllib
import hmac
from datetime import datetime
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bookseller.utils import count_cart


@app.route('/')
def index():
    cate_id = request.args.get('category_id')
    keyword = request.args.get('keyword')
    page = request.args.get("page", 1)
    page = int(page)
    products = utils.load_products(cate_id=cate_id, kw=keyword, page=page)
    counter = utils.cout_products()
    return render_template('index.html',products=products,page=math.ceil(counter/app.config['PAGE_SIZE']))

@app.route('/step/<int:step>', methods=['GET'])
def get_step(step):
    if step == 1:
        return render_template('cart.html')
    elif step == 2:
        return render_template('address.html')

    else:
        return "Invalid step", 404
@app.route("/products/<int:products_id>")
def products_detail(products_id):
    products = utils.get_products_by_id(products_id)

    products_detail = utils.get_products_detail_by_id(products_id)
    comments = utils.load_comments(products_id)
    counter=utils.count_comment(product_id=products_id)
    
    return render_template('products_detail.html', products=products, products_detail=products_detail,comments=comments,page=math.ceil(counter/ app.config['COMMENT_SIZE']))

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
@app.route("/address")

def address():
    return render_template('address.html')
# @app.route("/api/products/<product_id>/comments", methods=['post'])
# @login_required
# def add_comment(product_id):
#     c = utils.add_comment(content=request.json.get('content'), product_id=product_id)
#     return jsonify({
#         "id": c.id,
#         "content": c.content,
#         "created_date": c.created_date,
#         "user": {
#             "avatar": c.user.avatar
#         }
#     })

# @app.route("/products")
# def details():
#     data = request.json
#
#     product_id = data.get('product_id')
#     comments = utils.load_comments(product_id)
#     return render_template('details.html', product=utils.get_products_by_id(product_id))
@app.route('/api/comments', methods=['POST'])
@login_required
def add_comment():
    data = request.json
    content = data.get('content')
    product_id = data.get('product_id')

    try:
        c = utils.add_comment(content, product_id=product_id)


        return jsonify({
            'status': 200,
            'data': {
                "id": c.id,
                "content": c.content,
                'created_date': c.created_date,
                'user': {
                    'id': c.user.id,
                    'username': c.user.username,
                    'avatar': c.user.avatar
                }
            }
        })

    except Exception as e:

        return jsonify({
            'status': 404,
            'err_msg': f"Chương trình gặp lỗi: {str(e)}"
        })


@app.route('/api/products/<product_id>/comments',)
def get_comments(product_id):
    page = request.args.get('page', 1)
    comments=utils.get_comment(product_id=product_id,page=int(page))
    results=[]
    for c in comments:
        results.append({
            'id':c.id,
            'content':c.content,
            'created_date': str(c.created_date),
            'user':{
                'id':c.user.id,
                'username':c.user.username,
                'avatar':c.user.avatar
            }
        })
    return jsonify(results)

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


                utils.add_user(name=name,username=username,password=password,avatar=avatar_path,email=email)
                return redirect(url_for('user_singin'))
            else:
                err_msg="Đặt mật khẩu không khớp!!"
        except Exception as ex:
            err_msg="Hệ thống đang có lỗi"+str(ex)

    return render_template('register.html',err_msg=err_msg)

@app.route("/save_address", methods=["POST"])
def save_address():


    # Lấy dữ liệu từ form
    full_name = request.form.get("fullName")
    phone_number = request.form.get("phone")
    address = request.form.get("address")
    city = request.form.get("city")
    district = request.form.get("district")  # Quận/Huyện
    ward = request.form.get("ward")  # Xã/Phường
    country = "Vietnam"  # Mặc định Việt Nam
    is_default = True  # Có thể thêm logic nếu cần
@app.route("/add_address", methods=['GET', 'POST'])
def add_address():
    err_msg = ""
    user_id = current_user.id  # Lấy ID người dùng hiện tại từ Flask-Login

    # Kiểm tra xem người dùng đã có địa chỉ mặc định chưa
    address = DeliveryAddress.query.filter_by(user_id=user_id, is_default=True).first()

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        full_name = request.form.get('fullName', '').strip()
        phone_number = request.form.get('phone', '').strip()
        address_detail = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        district = request.form.get('district', '').strip()  # Không bắt buộc
        ward = request.form.get('ward', '').strip()  # Không bắt buộc
        country = "Vietnam"  # Mặc định
        is_default = True  # Mặc định đặt địa chỉ này làm chính

        try:
            # Kiểm tra các trường bắt buộc
            if not all([full_name, phone_number, address_detail, city]):
                err_msg = "Vui lòng điền đầy đủ các trường bắt buộc!"
            else:
                if address:  # Nếu đã có địa chỉ mặc định -> Cập nhật
                    address.full_name = full_name
                    address.phone_number = phone_number
                    address.address = address_detail
                    address.city = city
                    address.state = district
                    address.ward = ward
                else:  # Nếu chưa có địa chỉ -> Thêm địa chỉ mới
                    new_address = DeliveryAddress(
                        full_name=full_name,
                        phone_number=phone_number,
                        address=address_detail,
                        city=city,
                        state=district,
                        ward=ward,
                        country=country,
                        is_default=is_default,
                        user_id=user_id,
                    )
                    db.session.add(new_address)

                # Lưu thay đổi vào database
                db.session.commit()

                # Điều hướng sang bước tiếp theo (ví dụ: bước thanh toán)
                return redirect(url_for('pay_h'))

        except Exception as ex:
            # Ghi log và hiển thị thông báo lỗi
            app.logger.error(f"Lỗi khi thêm hoặc cập nhật địa chỉ: {ex}")
            err_msg = "Hệ thống đang gặp sự cố. Vui lòng thử lại sau!"

    # Render lại trang với thông báo lỗi nếu có
    return render_template('address.html', address=address, err_msg=err_msg)

@app.route("/cart")
def cart():
    return render_template('base1.html',stats=utils.count_cart(session.get('cart')))
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
    image=data.get('image')
    print(f"Image: {price}")
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
            'image': image,
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
@app.route('/pay')
def pay_h():
    user_id = current_user.id  # Lấy user_id từ current_user
    addresses = utils.get_user_addresses(user_id)  # Lấy tất cả địa chỉ của người dùng
    return render_template('pay.html',addresses=addresses)

@app.route('/api/pay', methods=['post'])
@login_required
def pay():
    try:

        utils.add_receipt(session.get('cart'))

        del session['cart']

    except:
        return jsonify({'code':400})
    return jsonify({'code':200})
@app.route('/api/pay1', methods=['post'])
@login_required
def pay1():
    try:
        user_id=current_user.id
        print(f"Current user: {current_user}")
        utils.add_receipt_unpaid(session.get('cart'))
        print("cc")
        utils.send_notification_email(user_id,subject = "Thông báo về tài khoản",body = "Xin chào, username của bạn đã tồn tại trong hệ thống. Vui lòng chọn username khác.")
        print("cc")
        del session['cart']

    except:
        return jsonify({'code':400})
    return jsonify({'code':200})

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
def get_payment_url(request_data, secret_key):
    # Sắp xếp dữ liệu theo thứ tự alphabe
    inputData = sorted(request_data.items())
    queryString = ''
    seq = 0
    for key, val in inputData:
        if seq == 1:
            queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
        else:
            seq = 1
            queryString = key + '=' + urllib.parse.quote_plus(str(val))

    # Tạo mã băm HMACSHA512
    hash_value = hmac.new(secret_key.encode('utf-8'), queryString.encode('utf-8'), hashlib.sha512).hexdigest()
    return f"{VNP_URL}?{queryString}&vnp_SecureHash={hash_value}"
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        cart = session.get('cart', {})
        cart_info = count_cart(cart)
        total_amount = cart_info['total_amount']  # Lấy total_quantity để làm amount
        order_type = "Bán Sach"
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(uuid.uuid4().int)[:6]
        order_desc = f"KaliLove Thanh Toán số tiền là {total_amount} VND"
        bank_code = "ncb"
        language = "vn"

        ipaddr = request.remote_addr
        txn_ref = order_id  # Mã giao dịch của bạn
        create_date = datetime.now().strftime('%Y%m%d%H%M%S')

        # Xây dựng requestData
        request_data = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': VNP_TMN_CODE,
            'vnp_Amount': total_amount * 100,  # VNPAY yêu cầu số tiền nhân 100
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': txn_ref,
            'vnp_OrderInfo': order_desc,
            'vnp_OrderType': order_type,
            'vnp_Locale': language if language else 'vn',
            'vnp_BankCode': bank_code if bank_code else '',
            'vnp_CreateDate': create_date,
            'vnp_IpAddr': ipaddr,
            'vnp_ReturnUrl': RETURN_URL,
        }

        # Lấy URL thanh toán
        payment_url = get_payment_url(request_data, VNP_HASH_SECRET)

        return redirect(payment_url)

    return render_template('pay.html')

@app.route('/payment_return', methods=['GET'])
def payment_return():
    input_data = request.args
    if input_data:
        vnp_secure_hash = input_data.get('vnp_SecureHash')
        vnp_transaction_no = input_data.get('vnp_TransactionNo')
        vnp_response_code = input_data.get('vnp_ResponseCode')

        # Xác thực mã băm
        request_data = {key: value for key, value in input_data.items() if key != 'vnp_SecureHash'}
        hash_value = hmac.new(VNP_HASH_SECRET.encode('utf-8'), urllib.parse.urlencode(request_data).encode('utf-8'), hashlib.sha512).hexdigest()

        if vnp_secure_hash == hash_value:
            if vnp_response_code == "00":
                return render_template('payment_return.html', result="Thành công", transaction_no=vnp_transaction_no)
            else:
                return render_template('payment_return.html', result="Lỗi", transaction_no=vnp_transaction_no)
        else:
            return render_template('payment_return.html', result="Sai mã băm", transaction_no=vnp_transaction_no)

    return render_template('payment_return.html', result="Không nhận được dữ liệu")


@app.route('/logout')
def logout_view():
    logout_user()
    return redirect('/login')




with app.app_context():
    result = utils.category_stats()
    print(result)

if __name__ == "__main__":
    from bookseller import admin
    app.run(debug=True)
