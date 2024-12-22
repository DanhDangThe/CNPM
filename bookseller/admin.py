from flask_admin.actions import action
from flask_login import logout_user, login_user
from sqlalchemy.sql.functions import current_user
from bookseller import app, db, utils
from bookseller.models import UserRole, Product, Category
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, AdminIndexView
from flask import redirect, request, render_template
from flask_login import current_user



class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

# class ProductView(AdminView):
#     column_display_pk = True


# class CategoryView(AdminView):
#     column_list = ['name', 'products']

class ProductView(AdminView):


    column_list = ['id', 'name']
    column_searchable_list = ['name']
    column_filters = ['id', 'name']
    column_editable_list = ['name']
    edit_modal = True



class CategoryView(AdminView):
    can_export = True
    column_searchable_list = ['id', 'name']
    column_filters = ['id', 'name']
    can_view_details = True
    column_list = ['name', 'products']





# class AuthenticatedUser(BaseView):
#     def is_accessible(self):
#         return current_user.is_authenticated


class LogoutView(AuthenticatedView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')





class ChangeRuleView(AuthenticatedView):
    @expose("/")
    def index(self):
        min_quantity = request.args.get('min_quantity')
        min_quantity_depot = request.args.get('min_quantity_depot')
        order_cancel_time = request.args.get('order_cancel_time')
        try:
            min_quantity = int(min_quantity)
            min_quantity_depot = int(min_quantity_depot)
            order_cancel_time = int(order_cancel_time)
        except:
            return self.render('/admin/changerule.html', err_msg='Thông tin không đúng. Vui lòng nhập lại!',
                               min_quantity=app.config['min_quantity'],
                               min_quantity_depot=app.config['min_quantity_depot'],
                               order_cancel_time=app.config['order_cancel_time'])
        if min_quantity>0 and min_quantity_depot>0 and order_cancel_time>0:
            app.config['min_quantity'] = min_quantity
            app.config['min_quantity_depot'] = min_quantity_depot
            app.config['order_cancel_time'] = order_cancel_time
            return self.render('/admin/changerule.html', err_msg='Thành công',
                               min_quantity=app.config['min_quantity'],
                               min_quantity_depot=app.config['min_quantity_depot'],
                               order_cancel_time=app.config['order_cancel_time'])
        else:
            return self.render('/admin/changerule.html', err_msg='Thông tin không đúng. Vui lòng nhập lại!',
                               min_quantity=app.config['min_quantity'],
                               min_quantity_depot=app.config['min_quantity_depot'],
                               order_cancel_time=app.config['order_cancel_time'])
        return self.render('/admin/changerule.html', err_msg='',
                           min_quantity=app.config['min_quantity'],
                           min_quantity_depot=app.config['min_quantity_depot'],
                           order_cancel_time=app.config['order_cancel_time'])

class StatsView(AuthenticatedView):
    @expose("/")
    def index(self):
        return self.render('admin/stats.html')



admin = Admin(app=app, name='Quản lý nhà sách', template_mode='bootstrap4')
admin.add_view(CategoryView(Category, db.session, name='Loại sách'))
admin.add_view(ProductView(Product, db.session, name='Sách'))
admin.add_view(ChangeRuleView(name='Thay đổi quy định'))
admin.add_view(StatsView(name='Thống kê báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))




