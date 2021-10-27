from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models_package.models import User
from app import app, db
from sqlalchemy import or_,and_,desc
import re,ast
from app.authentication import encode_auth_token,authentication
from app.serializer import query_serializer,comments_serializer, user_serializer,replace_with_ids,technology_serializer
from app.pagination import get_paginated_list
from app.utils.smtp_mail import send_mail_to_reset_password
from app.authentication import get_user_id

class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        email=data.get("email")
        mobile=data.get("mobile")
        password=data.get('password')
        if not ((email or mobile) and password):
            app.logger.info("email or mobile and password are required")
            return jsonify(status=400,message="email or mobile and password are required")
        user = db.session.query(User).filter(or_(User.email == email, User.mobile == mobile)).first()
        if user:
            if user.status == 0:
                app.logger.info("User is disabled temporarily")
                return jsonify(status=400,message="User is disabled temporarily")
            if user.roles == 2 or user.roles == 3 :
                if check_password_hash(user.password, password):
                    token = encode_auth_token(user)
                    app.logger.info(token)
                    response = user_serializer(user)
                    app.logger.info(f'{user.name} Logged in successfully')
                    return jsonify(status=200, data=response, message="Logged in successfully",
                                   token=token.decode('UTF-8'))
                else:
                    app.logger.info(f"{user.name} Incorrect password")
                    return jsonify(status=404, message="Incorrect password")
            else:
                app.logger.info(f"{user.name} Not allowed to login as admin")
                return jsonify(status=404,message="Not allowed to login as admin")
        else:
            app.logger.info(f"user not found")
            return jsonify(status=404,message="user not found")

class ForgotPassword(Resource):
    def post(self):
        data = request.get_json() or {}
        email = data.get("email")

        if not email:
            app.logger.info("email field is required")
            return jsonify(status=400,message="email field is required")

        else:
            try:
                user = User.query.filter(User.email == email).first()
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
                    app.logger.info(f'temporary password sent to {user.email}')
                    return jsonify(status=200, message=f'temporary password sent to {user.email}')
                app.logger.info("User not found")
                return jsonify(status=400, message="User not found")
            except:
                app.logger.info("database error")
                return jsonify(status=400, message="database error")

class UserStatus(Resource):
    @authentication
    def put(self):
        data = request.get_json() or {}
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        user_id = data.get('user_id')
        change_user_id = data.get('change_user_id')
        change_user_role = data.get('change_user_role')
        if not (change_user_id and user_id and change_user_role):
            app.logger.info("change_user_id and user id and change_user_role are required fields")
            return jsonify(status=404, message="change_user_id and user id and change_user_role are required fields")
        user_check = User.query.filter_by(id=user_id).first()
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
    @authentication
    def delete(self):
        user_id = get_user_id(self)
        delete_user = request.args.get('delete_user_id')
        if not delete_user:
            app.logger.info("delete_user_id is required")
            return jsonify(status=404, message="delete_user_id is required")
        user_check = User.query.filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        delete_user = User.query.filter_by(id=delete_user).first()
        if not delete_user:
            app.logger.info("User you wanted to delete not found")
            return jsonify(status=400, message="User you wanted to delete not found")

        if user_check.roles == 3:
            if delete_user.status:
                delete_user.status = False
            else:
                delete_user.status = True
            today = datetime.now()
            date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            delete_user.updated_at = date_time_obj
            db.session.commit()
            app.logger.info("success")
            return jsonify(status=200, message="success")
        app.logger.info("User not allowed to perform this action")
        return jsonify(status=404, message="User not allowed to perform this action")


class GetProfile(Resource):
    def get(self,user_id):
        user_data=User.query.filter_by(id=user_id).first()
        if not user_data:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        return jsonify(status=200,data=user_serializer(user_data),message="user data")


class GetAllUsers(Resource):
    @authentication
    def get(self):
        dt = {}
        users_list = []
        user_id = get_user_id(self)
        user_check=User.query.filter_by(id=user_id).first()
        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("only admin or superadmin are allowed")
            return jsonify(status=400, message="only admin or superadmin are allowed")
        users = User.query.filter_by(roles=1).all()
        if not users:
            app.logger.info("No users in db")
            return jsonify(status=400, message="No users in db")
        for itr in users:
            dt = {
                'name': itr.name,
                'user_id': itr.id
            }
            users_list.append(dt)
            # print(users_list)
        return jsonify(status=200, data=get_paginated_list(users_list, '/admin/getallusers', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 10),with_params=False),
                       message="Returning all user's name and ids")

class UserSearch(Resource):
    def get(self):
        name=request.args.get('name')
        if not name:
            app.logger.info('name required')
            return jsonify(status=400,message="name required")
        user_obj = User.query.filter(User.name.ilike(f'%{name}%')).all()
        if not user_obj:
            app.logger.info("User not found")
            return jsonify(status=404, message="user not found")
        user_list = []
        for itr in user_obj:
            dt = user_serializer(itr)
            user_list.append(dt)
        if not user_list:
            app.logger.info("No records found")
            return jsonify(status=404,message="No records found")
        page = f"/usersearch?name={name}"
        app.logger.info("Returning user data")
        return jsonify(status=200,
            data=user_list, message="Returning user data")
        # return jsonify(status=200,
        #     data=get_paginated_list(user_list, page, start=request.args.get('start', 1),
        #     limit=request.args.get('limit', 3),with_params=False), message="Returning user data")


# class GetUserByName(Resource):
#     def get(self):
#
#         users = User.query.filter_by(roles=1).all()
#         if not users:
#             app.logger.info("No users in db")
#             return jsonify(status=400, message="No users in db")
#         for itr in users:
#             dt = {
#                 'name': itr.name,
#                 'user_id': itr.id
#             }
#             users_list.append(dt)
#             print(users_list)
#         return jsonify(status=200, data=get_paginated_list(users_list, '/admin/getallusers', start=request.args.get('start', 1),
#                                                            limit=request.args.get('limit', 3)),
#                        message="Returning all user's name and ids")





# from flask_restplus import Resource
#
# class UsersCRUD(Resource):
#     def get(self):
#         pass
#
#     def put(self):
#         pass
#
#     def post(self):
#         pass
#
#     def delete(self):
#         pass
#
# class SuperUserActions(Resource):
#     def put(self):  # change user roles
#         pass
#
#     def delete(self):  # soft delete user (change status)
#         pass
#
#
# class SuperAdmin(Resource):
#     def put(self):  # change user roles
#         pass
#
#     def delete(self):  # delete users
#         pass
#
#
# class PriviligedTasks(Resource):
#     def put(self):  # change queries comments by id
#         pass
#
#     def delete(self):  # delete queries comments by id
#         pass
#
