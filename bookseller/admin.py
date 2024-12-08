from flask_login import logout_user, login_user
from sqlalchemy.sql.functions import current_user
from bookseller import app, db, utils
from bookseller.models import UserRole
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, AdminIndexView
from flask import redirect, request, render_template
from flask_login import current_user



class AuthenticatedAdmin(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class Authenticated_Admin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedUser):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')



class ChangRuleView(BaseView):
    @expose("/")
    def index(self):
        min_quantity =request.args.get('min_quantity')
        min_quantity_stock = request.args.get('min_quantity_stock')
        order_cancel_time = request.args.get('order_cancel_time')
        try:
            min_quantity = int(min_quantity)
            min_quantity_stock = int(min_quantity_stock)
            order_cancel_time = int(order_cancel_time)
        except:
            return self.render('admin/changerule.html', err_msg='Thông tin không hợp lê. Vui lòng nhập lại!!')
        if min_quantity>=150 and min_quantity_stock<300:
            return self.render('admin/changerule.html', err_msg='Thành công')
        else:
            return self.render('admin/changerule.html', err_msg='Thông tin không hợp lệ. Vui lòng nhập lại!!')
        return self.render('admin/changerule.html', err_msg='Vui lòng nhập thông tin!!')



class StatsView(BaseView):
    @expose("/")
    def index(self):
        return self.render('admin/stats.html')


admin = Admin(app=app, name='Quản lý nhà sách', template_mode='bootstrap4')
admin.add_view(ChangRuleView(name='Thay đổi quy định'))
admin.add_view(StatsView(name='Thống kê báo cáo'))



