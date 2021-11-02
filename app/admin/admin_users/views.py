from flask import jsonify, request
from flask_restplus import Resource
from datetime import datetime
from app.models_package.models import User,Roles
from werkzeug.security import generate_password_hash,check_password_hash
import re
from app import app, db
from app.authentication import authentication
from app.authentication import get_user_id,is_active
from app.pagination import get_paginated_list
from sqlalchemy import or_
from app.serializer import role_serializer,replace_with_ids,user_serializer
from app.utils.form_validation import *
class AdminUserDetails(Resource):
   @authentication
   def get(self):
       admin_user_id=request.args.get('admin_user_id')
       user_id = get_user_id(self)
       admin = User.query.filter_by(id=user_id).first()
       if not admin:
           app.logger.info("Admin not found")
           return jsonify(status=404, message="Admin not found")
       if not is_active(user_id):
           app.logger.info("User is temporarily disabled")
           return jsonify(status=404, message="User is temporarily disabled")
       if admin.roles == 1:
           app.logger.info("User can not view the details")
           return jsonify(status=404, message="User can not view the details")

       user_data = db.session.query(User).filter_by(id=admin_user_id).first()

       if (not user_data) or (not (user_data.roles == 2 or user_data.roles ==3)):
           app.logger.info("Admin not found")
           return jsonify(status=400, message="Admin not found")

       return jsonify(status=200, data=user_serializer(user_data), message="user data")

class EditProfile(Resource):
    @authentication
    def put(self):
        data = request.get_json() or {}
        user_id = get_user_id(self)
        user_update = User.query.filter_by(id=user_id).first()
        if not user_update:
            app.logger.info("User not found")
            return jsonify(status=404, message="User not found")
        if user_update.roles == 1:
            app.logger.info("User can not change")
            return jsonify(status=404, message="User can not change")
        name = data.get('name')
        technology = data.get('technology')
        if not is_active(user_id):
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, message="User is temporarily disabled")
        if not (name and technology):
            app.logger.info("name, technology are required")
            return jsonify(status=400, message="name, technology are required")


        elif not name_validator(name):
            msg = 'Invalid name'
            app.logger.info(msg)
            return jsonify(status=404, message=msg)
        else:
            if not user_update.name == name:
                user_update.name = name
            ids_list = f"{replace_with_ids(technology)}"
            user_update.technology = ids_list
            today = datetime.now()
            user_update.date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            db.session.commit()
            response = {"name": user_update.name, "technology": technology}
            app.logger.info(f'{user_update.name} Updated successfully')
            return jsonify(status=200, data=response, message="updated Successfully")


class ChangePassword(Resource):
    @authentication
    def put(self):
        user_id = get_user_id(self)
        user = User.query.filter_by(id=user_id).first()
        if not user:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        if not is_active(user_id):
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, message="User is temporarily disabled")

        if user.roles == 1:
            app.logger.info("User can not change")
            return jsonify(status=404, message="User can not change")

        data = request.get_json() or {}
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        confirm_new_password = data.get("confirm_new_password")

        if not (old_password and new_password and confirm_new_password):
            app.logger.info(f'old_password, new_password and confirm_new_password required')
            return jsonify(status=400, message="old_password, new_password and confirm_new_password required")
        try:
            if check_password_hash(user.password, data.get('old_password')):
                if new_password == confirm_new_password:
                    if new_password == old_password:
                        app.logger.info("New password and old password should not be same")
                        return jsonify(status=400, message="New password and old password should not be same")
                    if not password_validator(new_password):
                        app.logger.info("Invalid password")
                        return jsonify(status=400,
                                       message='Invalid password')
                    user.password = generate_password_hash(new_password, method='sha256')
                    db.session.commit()
                    app.logger.info(f'{user.name} Password updated successfully')
                    return jsonify(status=200, message="Password updated successfully")
                else:
                    app.logger.info(f'{user.name} New password and confirm new password doesnt match')
                    return jsonify(status=200, message="New password and confirm new password doesn't match")
            else:
                app.logger.info(f"{user.name} Incorrect old password")
                return jsonify(status=404, message="Incorrect old password")
        except:
            app.logger.info("Unknown database")
        return jsonify(status=404, message="Unknown database")

class RolesClass(Resource):
    @authentication
    def get(self): #get all roles
        user_id = get_user_id(self)
        if not user_id:
            app.logger.info("login required")
            return jsonify(status=400, message="login required")
        if not is_active(user_id):
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, message="User is temporarily disabled")
        check_super_admin = User.query.filter_by(id=user_id).first()
        if not check_super_admin:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if check_super_admin.roles == 3:
            list_of_roles=[]
            get_roles=Roles.query.all()
            for itr_role in get_roles:
                list_of_roles.append(role_serializer(itr_role))
            app.logger.info("Returning user roles")
            return jsonify(status=400, data=list_of_roles,message="Returning user roles")
        app.logger.info("only superadmin can make changes")
        return jsonify(status=400, message="only superadmin can make changes")
    @authentication
    def put(self): #edit new role
        data = request.get_json() or {}
        edited_role = data.get('edited_role')
        role_id=data.get('role_id')
        user_id = get_user_id(self)
        if not user_id:
            app.logger.info("login required")
            return jsonify(status=400, message="login required")
        if not is_active(user_id):
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, message="User is temporarily disabled")
        if not (edited_role and role_id):
            app.logger.info("edited_role, role_id are required fields")
            return jsonify(status=400, message="edited_role, role_id are required fields")
        check_super_admin = User.query.filter_by(id=user_id).first()
        if not check_super_admin:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if check_super_admin.roles == 3:
            check_role_exists = Roles.query.filter_by(id=role_id).first()
            if check_role_exists:
                check_role_exists.name=edited_role
                db.session.commit()
            app.logger.info("role edited")
            return jsonify(status=200, message="role edited")
        app.logger.info("only superadmin can make changes")
        return jsonify(status=400, message="only superadmin can make changes")
    @authentication
    def post(self): #add new role
        data=request.get_json() or {}
        new_role=data.get('new_role')
        user_id=get_user_id(self)
        if not new_role:
            app.logger.info("new_role is required fields")
            return jsonify(status=400, message="new_role is required fields")
        if not is_active(user_id):
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, message="User is temporarily disabled")
        check_super_admin=User.query.filter_by(id=user_id).first()
        if not check_super_admin:
            app.logger.info("user not found")
            return jsonify(status=400,message="user not found")
        if check_super_admin.roles == 3:
            check_role_exists=Roles.query.filter(Roles.name.ilike(f"{new_role}")).first()
            if check_role_exists:
                app.logger.info("role already exists")
                return jsonify(status=400, message="role already exists")
            today = datetime.now()
            date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            add_role = Roles(new_role, date_time_obj, date_time_obj)
            db.session.add(add_role)
            db.session.commit()
            app.logger.info("role added succesfully")
            return jsonify(status=200, message="role added succesfully")
    @authentication
    def delete(self):
        data = request.get_json() or {}
        role_id = data.get('role_id')
        user_id = get_user_id(self)
        if not user_id:
            app.logger.info("login required")
            return jsonify(status=400, message="login required")
        if not role_id:
            app.logger.info("role_id is required field")
            return jsonify(status=400, message="role_id is required field")
        if not is_active(user_id):
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, message="User is temporarily disabled")
        check_super_admin = User.query.filter_by(id=user_id).first()
        if not check_super_admin:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if check_super_admin.roles == 3:
            check_role_exists = Roles.query.filter_by(id=role_id).first()
            if check_role_exists:
                if check_role_exists.status:
                    check_role_exists.status = 0
                else:
                    check_role_exists.status= 1
                db.session.commit()
            app.logger.info("role deleted")
            return jsonify(status=200, message="role deleted")
        app.logger.info("only superadmin can delete")
        return jsonify(status=400, message="only superadmin can delete")

class AdminUsersEditDel(Resource):
    @authentication
    def put(self):  # edit admin users
        user_id = get_user_id(self)
        data = request.get_json() or {}
        change_user_id = data.get('change_user_id')
        new_role = data.get('new_role')
        if not (change_user_id and new_role):
            app.logger.info("change_user_id and new_role are required")
            return jsonify(status=400, message="change_user_id and new_role are required")
        if not is_active(user_id):
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, message="User is temporarily disabled")
        check_superadmin = User.query.filter_by(id=user_id).first()
        check_admin = User.query.filter_by(id=change_user_id).first()

        if not check_superadmin:
            app.logger.info("superadmin not found")
            return jsonify(status=404, message="superadmin not found")
        if not check_admin:
            app.logger.info("admin not found")
            return jsonify(status=404, message="admin not found")
        if check_superadmin.roles != 3:
            app.logger.info("only superadmin can edit")
            return jsonify(status=404, message="only superadmin can edit")
        if new_role == 3:
            app.logger.info("can't add superadmins")
            return jsonify(status=404, message="can't add superadmins")
        if check_superadmin.roles == 3 and  check_admin.roles != 3:
            check_admin.roles = new_role
            today = datetime.now()
            check_admin.date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            db.session.commit()
            response = {"name": check_admin.name, "role": check_admin.roles}
            app.logger.info(f'{check_admin.name} Updated successfully')
            return jsonify(status=200, data=response, message="updated Successfully")
        app.logger.info("only admins are editable")
        return jsonify(status=404, message="only admins are editable")
    @authentication
    def delete(self):  # delete admin users
        user_id = get_user_id(self)
        data = request.get_json() or {}
        delete_user_id = data.get('delete_user_id')
        if not delete_user_id:
            app.logger.info("delete_user_id required")
            return jsonify(status=400, message="delete_user_id required")
        if not is_active(user_id):
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, message="User is temporarily disabled")
        check_superadmin = User.query.filter_by(id=user_id).first()
        check_admin = User.query.filter_by(id=delete_user_id).first()
        if not check_superadmin:
            app.logger.info("superadmin not found")
            return jsonify(status=404, message="superadmin not found")
        if not check_admin:
            app.logger.info("admin not found")
            return jsonify(status=404, message="admin not found")
        if check_superadmin.roles != 3:
            app.logger.info("only superadmin can delete")
            return jsonify(status=404, message="only superadmin can delete")
        if check_admin.roles != 2:
            app.logger.info("only admin can be deleted")
            return jsonify(status=404, message="only admin can be deleted")
        if check_superadmin.roles == 3 and (check_admin.roles != 1 or check_admin.roles != 3):
            if check_admin.status:
                check_admin.status = False
            else:
                check_admin.status = True
            today = datetime.now()
            check_admin.date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            db.session.commit()
            response = {"name": check_admin.name, "status": check_admin.status}
            app.logger.info('success')
            return jsonify(status=200, data=response, message="success")


class GetAllAdminUsers(Resource):
    @authentication
    def get(self):
        dt = {}
        users_list = []
        user_id=get_user_id(self)
        check_user=User.query.filter_by(id=user_id).first()
        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if not is_active(user_id):
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, message="User is temporarily disabled")
        if not (check_user.roles==2 or check_user.roles==3):
            app.logger.info("only admin or superadmin are allowed")
            return jsonify(status=400, message="only admin or superadmin are allowed")
        users = User.query.filter(or_(User.roles==2,User.roles==3)).all()
        if not users:
            app.logger.info("No users in db")
            return jsonify(status=400, message="No users in db")
        for itr in users:
            admin_user_data=user_serializer(itr)
            # dt = {
            #     'name': itr.name,
            #     'user_id': itr.id,
            #     'role':itr.roles
            # }
            users_list.append(admin_user_data)
        return jsonify(status=200, data=get_paginated_list(users_list, '/admin/getalladminusers', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 10),with_params=False),
                       message="Returning all user's name and ids")

