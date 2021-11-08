from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments
from app import app, db
from sqlalchemy import or_, and_, desc
import re, ast
from werkzeug.security import generate_password_hash, check_password_hash
from app.authentication import encode_auth_token, authentication
from app.user.serilalizer.serilalizer import user_serializer,replace_with_ids
from app.user.pagination.pagination import get_paginated_list
from app.utils.smtpmail import send_mail_to_reset_password,generate_temp_password_and_check
from app.utils.form_validations import name_validator,password_validator,email_validator,number_validation,title_validator
from app.authentication import get_user_id,authentication,is_active


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        email = data.get("email")
        mobile = data.get("mobile")
        password = data.get('password')
        if not ((email or mobile) and password):
            app.logger.info("email or mobile and password are required")
            return jsonify(status=400, message="email or mobile and password are required")
        user = db.session.query(User).filter(or_(User.email == email, User.mobile == mobile)).first()
        if user:
            if user.status == 0:
                app.logger.info("User is disabled temporarily")
                return jsonify(status=400, message="User is disabled temporarily")
            if check_password_hash(user.password, password):
                token = encode_auth_token(user)
                app.logger.info(token)
                response = user_serializer(user)
                User.login=True
                db.session.commit()
                app.logger.info(f'{user.name} Logged in successfully')
                return jsonify(status=200, data=response, message="Logged in successfully", token=token.decode('UTF-8'))
            else:
                app.logger.info(f"{user.name} Incorrect password")
                return jsonify(status=404, messsage="Incorrect password")
        else:
            app.logger.info(f"user not found")
            return jsonify(status=404, message="user not found")


class Logout(Resource):
    def post(self):
        app.logger.info("Logged out successfully")
        return jsonify(status=200, message="Logged out successfully")

    def get(self):
        app.logger.info("Logged out successfully")
        return jsonify(status=200, message="Logged out successfully")


class Register(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        name = data.get('name')
        email = data.get('email')
        mobile = data.get('mobile')
        list_of_tech = data.get('technology')
        password = data.get("password")
        # check all data exists or not
        # if not (name and email and mobile and list_of_tech and password):
        #     msg = 'name, email, mobile, technology and password are required fields'
        # check valid email
        # elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        #     msg = 'Invalid email address'
        # elif not (re.match(r'[0-9]+', mobile) and len(mobile) == 10):
        #     msg = 'Invalid phone number'
        #  check valid name
        # elif not re.match(r'[A-Za-z0-9]+', name):
        #     msg = 'Name must contain only characters and numbers'
        # elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$', password):
        #     msg = 'Password should contain min 8 characters, a special character, Uppercase, lowercase and a number'
        # check user already exist
        if not (name and email and mobile and list_of_tech and password):
            msg = 'name, email, mobile, technology and password are required fields'
            # check valid name
        elif not name_validator(name):
            msg = 'Invalid name'
            # check valid email
        elif not email_validator(email):
            msg = 'Invalid email address'
        elif not number_validation(mobile):
            msg = 'Invalid phone number'
        elif not password_validator(password):
            msg = 'Invalid password'
        else:
            try:
                user = User.query.filter(or_(User.email == email,
                                             User.mobile == mobile,
                                             User.name == name)).first()
                if user:
                    msg = 'User already exist'
                else:
                    ids_list = f"{replace_with_ids(list_of_tech)}"
                    # technology = ast.literal_eval(technology)
                    today = datetime.now()
                    date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                    password = generate_password_hash(password, method='sha256')
                    status=True
                    user = User(name, email, mobile, ids_list, password,status,date_time_obj, date_time_obj)
                    db.session.add(user)
                    db.session.commit()
                    response = {"name": name, "email": email, "mobile": mobile, "technology": list_of_tech}
                    app.logger.info(f'{user.name} Registered successfully')
                    return jsonify(status=200, data=response, message="Registered successfully")
            except:
                app.logger.info("Database connection not established")
                return jsonify(status=404, message="Database connection not established")
        app.logger.info(msg)
        return jsonify(status=400, message=msg)


class UpdatePassword(Resource):
    @authentication
    def put(self):
        data = request.get_json() or {}
        email = data.get("email")
        mobile = data.get("mobile")
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        confirm_new_password = data.get("confirm_new_password")

        if not ((email or mobile) and (old_password and new_password and confirm_new_password)):
            app.logger.info(f'email (or) mobile , old_password, new_password and confirm_new_password required')
            return jsonify(status=400,
                           message="email (or) mobile , old_password, new_password and confirm_new_password required")
        if not password_validator(password):
            msg = 'Invalid password'
            app.logger.info(msg)
            return jsonify(status=400,message=msg)
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        try:
            user = db.session.query(User).filter(or_(User.email == email, User.mobile == data.get("mobile"))).first()
            if user:

                if check_password_hash(user.password, data.get('old_password')):
                    if new_password == confirm_new_password:
                        if new_password == old_password:
                            app.logger.info("New password and old password should not be same")
                            return jsonify(status=400, message="New password and old password should not be same")
                        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$',
                                        new_password):
                            app.logger.info(
                                "Password should contain min 8 characters, a special character, Uppercase, lowercase and a number")
                            return jsonify(status=400,
                                           message='Password should contain min 8 characters, a special character, Uppercase, lowercase and a number')
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
            else:
                app.logger.info("User not found")
                return jsonify(status=404, message="User not found")
        except:
            app.logger.info("Unknown database")
            return jsonify(status=404, message="Unknown database")

class ForgotPassword(Resource):
    def post(self):
        data = request.get_json() or {}
        email = data.get("email")
        mobile = data.get("mobile")

        if not (email and mobile):
            app.logger.info("email, mobile fields are required")
            return jsonify(status=400, message="email, mobile fields are required")
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        else:
             try:
                user = db.session.query(User).filter(and_(User.email == email, User.mobile == mobile)).first()
                if user:
                    new_password = send_mail_to_reset_password(user.email, user.name)
                    if new_password == 'Error':
                        app.logger.info("mail sending failed")
                        return jsonify(status=400, message="mail sending failed")
                    app.logger.info(f"Email sent successfully to {user.email}")
                    today = datetime.now()
                    date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                    user.updated_at = date_time_obj
                    user.password = generate_password_hash(new_password, method='sha256')
                    db.session.commit()
                    app.logger.info(f'{user.name} password changed  successfully')
                    return jsonify(status=200, message="password changed  successfully")
                app.logger.info("user not found")
                return jsonify(status=400, message="user not found")
             except:
                app.logger.info("database error")
                return jsonify(status=400, message="database error")
            


class UserProfile(Resource):
    @authentication
    def get(self):
        user_id=get_user_id(self)
        if not user_id:
            app.logger.info("user_id required")
            return jsonify(status=400,message="user_id required")
        user_data=db.session.query(User).filter_by(id=user_id).first()
        if not user_data:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        return jsonify(status=200,data=user_serializer(user_data),message="user data")

    def put(self):
        data = request.get_json() or {}
        try:
            user_id=get_user_id(self)
            user_update = User.query.filter_by(id = user_id).first()
        except:
            app.logger.info("User not found")
            return jsonify(status=404, message="user not found")
        name = data.get('name')
        technology = data.get('technology')

        if not (name  and technology):
            app.logger.info("name and technology are required")
            return jsonify(status=400, message="name and technology are required")
        if not name_validator(name):
            msg = 'Invalid name'
            app.logger.info(msg)
            return jsonify(status=404,message=msg)
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        else:
            if user_update:
                if not user_update.name == name:
                    user_update.name = name
                else:
                 app.logger.info("new name should be taken")
                 return jsonify(status=400,message="new name should be taken")
                tech_list=[]
                for itr in technology:
                    tech_check=Technologies.query.filter_by(name=itr).first()
                    if tech_check:
                        tech_list.append(tech_check.id)
                user_update.technology=f"{tech_list}"
                today = datetime.now()
                user_update.date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                db.session.commit()
                response = {"name": user_update.name, "technology": technology}
                app.logger.info(f'{user_update.name} Updated successfully')
                return jsonify(status=200, data=response, message="updated Successfully")


class UserStatus(Resource):
    @authentication
    def put(self):
        data = request.get_json() or {}
        user_id = get_user_id(self)
        change_user_id = data.get('change_user_id')
        change_user_role = data.get('change_user_role')
        if not (change_user_id and change_user_role):
            app.logger.info("change_user_id and change_user_role are required fields")
            return jsonify(status=404, message="change_user_id and change_user_role are required fields")
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        change_user_role = db.session.query(User).filter_by(id=change_user_id).first()
        if not change_user_role:
            app.logger.info("User you wanted to change role not found")
            return jsonify(status=400, message="User you wanted to change role not found")
        active=is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        if user_check.roles == 2:
            change_user_role.roles = 2
            today = datetime.now()
            date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            change_user_role.updated_at = date_time_obj
            db.session.commit()
            app.logger.info(f"{change_user_role.name} role changed successfully")
            return jsonify(status=200, message=f"{change_user_role.name} role changed successfully")
        app.logger.info("User not allowed to perform this action")
        return jsonify(status=404, message="User not allowed to perform this action")

    @authentication
    def delete(self):
        data = request.get_json() or {}
        user_id = get_user_id(self)
        delete_user = data.get('delete_user_id')
        if not (delete_user):
            app.logger.info("delete_user required")
            return jsonify(status=404, message="delete_user_id required")
        user_check = db.session.query(User).filter_by(id=user_id).first()
        # if not user_check:
        #     app.logger.info("User not found")
        #     return jsonify(status=400, message="User not found")
        delete_user = db.session.query(User).filter_by(id=delete_user).first()
        if not delete_user:
            app.logger.info("User wanted to delete not found")
            return jsonify(status=400, message="User wanted to delete not fou=d")
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        if user_check.roles == 2 or user_check.roles == 3:
            delete_user.status = 0
            today = datetime.now()
            date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            delete_user.updated_at = date_time_obj
            db.session.commit()
            app.logger.info(f"{delete_user} disabled successfully")
            return jsonify(status=200, message=f"{delete_user} disabled successfully")
        app.logger.info("User not allowed to perform this action")
        return jsonify(status=404, message="User not allowed to perform this action")

