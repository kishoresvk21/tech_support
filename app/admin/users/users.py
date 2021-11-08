from flask import jsonify, request
from sqlalchemy.future import select
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from sqlalchemy.orm import query
from sqlalchemy.sql.expression import delete
from sqlalchemy.sql.functions import user
from werkzeug.security import generate_password_hash, check_password_hash
from app.user.models.models import User, Technologies, Queries, Comments, Opinion
from app import app, db
from sqlalchemy import or_,and_,desc
import re,ast
from app.authentication import encode_auth_token,authentication
#is_admin_or_superadmin
from app.user.serilalizer.serilalizer import query_serializer,comments_serializer, user_serializer,replace_with_ids,technology_serializer
from app.user.pagination.pagination import get_paginated_list
from app.utils.smtpmail import send_mail_to_reset_password
from app.utils.form_validations import name_validator,password_validator,email_validator,number_validation,title_validator

class AdminLogin(Resource):
    def post(self):
        data = request.get_json() or {}
        email=data.get("email")
        mobile=data.get("mobile")
        password=data.get('password')
        if not ((email or mobile) and password):
            app.logger.info("email or mobile and password are required")
            return jsonify(status=400,message="email or mobile and password are required")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        user = db.session.query(User).filter(or_(User.email == email, User.mobile == mobile)).first()
        if user:
            if user.role!=1:
                if check_password_hash(user.password, password):
                    token = encode_auth_token(user)
                    app.logger.info(token)
                    response = user_serializer(user)
                    app.logger.info(f'{user.name} Logged in successfully')
                    return jsonify(status=200, data=response, message="Logged in successfully",
                                   token=token.decode('UTF-8'))
                else:
                    app.logger.info(f"{user.name} Incorrect password")
                    return jsonify(status=404, messsage="Incorrect password")
            else:
                app.logger.info(f"{user.name} Not allowed to login as admin")
                return jsonify(status=404,messsage="Not allowed to login as admin")
        else:
            app.logger.info(f"user not found")
            return jsonify(status=404,message="user not found")


class AdminForgotPassword(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        mobile = data.get("mobile")

        if not (email and mobile):
            app.logger.info("email, mobile fields are required")
            return jsonify(status=400,message="email, mobile fields are required")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        else:
            try:
                user = db.session.query(User).filter(and_(User.email == email, User.mobile == mobile)).first()
                if user:
                    new_password = send_mail_to_reset_password(user.email, user.name)
                    if new_password == 'Error':
                        app.logger.info("mail sending failed")
                        return jsonify(status=400,message="mail sending failed")
                    app.logger.info("Email sent successfully")
                    today = datetime.now()
                    date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                    user.updated_at = date_time_obj
                    user.password = generate_password_hash(new_password, method='sha256')
                    db.session.commit()
                    app.logger.info(f'{user.name} password changed  successfully')
                    return jsonify(status=200, message="password changed  successfully")
                app.logger.info("cannot change password")
                return jsonify(status=400, message="cannot change password")
            except:
                app.logger.info("database error")
                return jsonify(status=400, message="database error")


class UserStatus(Resource):
    # @authentication
    def put(self):
        data = request.get_json() or {}
        user_id = data.get('user_id')
        change_user_id = data.get('change_user_id')
        change_user_role = data.get('change_user_role')
        if not (change_user_id and user_id and change_user_role):
            app.logger.info("change_user_id and user id and change_user_role are required fields")
            return jsonify(status=404, message="change_user_id and user id and change_user_role are required fields")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        change_user_role_check = db.session.query(User).filter_by(id=change_user_id).first()
        if not change_user_role:
            app.logger.info("User you wanted to change role not found")
            return jsonify(status=400, message="User you wanted to change role not found")

        if user_check.roles == 3:
            change_user_role_check.roles = change_user_role
            today = datetime.now()
            date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            change_user_role_check.updated_at = date_time_obj
            db.session.commit()
            app.logger.info(f"{change_user_role_check.name} role changed successfully")
            return jsonify(status=200, message=f"{change_user_role_check.name} role changed successfully")
        app.logger.info("User not allowed to perform this action")
        return jsonify(status=404, message="User not allowed to perform this action")


class UserDelete(Resource):
    # @authentication
    def delete(self):
        data = request.get_json() or {}
        user_id = data.get('user_id')
        delete_user = data.get('delete_user_id')
        if not (delete_user and user_id):
            app.logger.info("delete_user_id and User id are required fields")
            return jsonify(status=404, message="delete_user_id and User id are required fields")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        delete_user = db.session.query(User).filter_by(id=delete_user).first()
        if not delete_user:
            app.logger.info("User wanted to delete not found")
            return jsonify(status=400, message="User wanted to delete not found")

        if user_check.roles!=1:
            delete_user.status = 0  # changed from roles to status (soft delete)
            today = datetime.now()
            date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            delete_user.updated_at = date_time_obj
            db.session.commit()
            app.logger.info(f"{delete_user} disabled successfully")
            return jsonify(status=200, message=f"{delete_user} disabled successfully")
        app.logger.info("User not allowed to perform this action")
        return jsonify(status=404, message="User not allowed to perform this action")


class GetProfile(Resource):
    def get(self,user_id):

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        user_data=db.session.query(User).filter_by(id=user_id).first()
        if not user_data:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        return jsonify(status=200,data=user_serializer(user_data),message="user data")


class GetAllUsers(Resource):
    def get(self):

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        users_list = []

        users = User.query.filter_by(roles=1).all()
        if not users:
            app.logger.info("No users found")
            return jsonify(status=400, message="No users found")
        for itr in users:
            dt = {
                'name': itr.name,
                'user_id': itr.id
            }
            users_list.append(dt)
            print(users_list)
        return jsonify(status=200, data=get_paginated_list(users_list, '/getallusers', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3)),
                       message="Returning all user's name and ids")

class AdminRoles(Resource):
    @authentication
    def get(self): #get all roles
        user_id = get_user_id(self)
        if not user_id:
            app.logger.info("login required")
            return jsonify(status=400, message="login required")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        check_super_admin = User.query.filter_by(id=user_id).first()
        if not check_super_admin:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if check_super_admin.roles == 3:
            list_of_roles=[]
            get_roles=Roles.query.all()
            for itr_role in get_roles:
                list_of_roles.append(role_serializer(itr_role))



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
        if not (edited_role and role_id):
            app.logger.info("edited_role, role_id are required fields")
            return jsonify(status=400, message="edited_role, role_id are required fields")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

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
            return jsonify(status=400, message="role edited")
        app.logger.info("only superadmin can make changes")
        return jsonify(status=400, message="only superadmin can make changes")
    @authentication
    def post(self): #add new role
        data=request.get_json() or {}
        new_role=data.get('new_role')
        user_id=get_user_id(self)
        if not (new_role and user_id):
            app.logger.info("new_role and user_id are required fields")
            return jsonify(status=400, message="new_role and user_id are required fields")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

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

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        check_super_admin = User.query.filter_by(id=user_id).first()
        if not check_super_admin:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if check_super_admin.roles == 3:
            check_role_exists = Roles.query.filter_by(id=role_id).first()
            if check_role_exists:
                check_role_exists.status = 0
                db.session.commit()
            app.logger.info("role deleted")
            return jsonify(status=400, message="role deleted")
        app.logger.info("only superadmin can delete")
        return jsonify(status=400, message="only superadmin can delete")
