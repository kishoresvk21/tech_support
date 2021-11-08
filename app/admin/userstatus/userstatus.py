
from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments
from app import app, db
from sqlalchemy import or_, and_, desc
import re, ast
from app.authentication import encode_auth_token, authentication,is_active
from app.user.serilalizer.serilalizer import technology_serializer,replace_with_ids
from app.user.pagination.pagination import get_paginated_list

class UserStatus(Resource):
    @authentication
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

        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        change_user_role = db.session.query(User).filter_by(id=change_user_id).first()
        if not change_user_role:
            app.logger.info("User you wanted to change role not found")
            return jsonify(status=400, message="User you wanted to change role not found")

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
        user_id = data.get('user_id')
        delete_user = data.get('delete_user_id')
        if not (delete_user and user_id):
            app.logger.info("delete_user_id and User id are required fields")
            return jsonify(status=404, message="delete_user_id and User id are required fields")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")

        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        delete_user = db.session.query(User).filter_by(id=delete_user).first()
        if not delete_user:
            app.logger.info("User wanted to delete not found")
            return jsonify(status=400, message="User wanted to delete not found")

        if user_check.roles == 2 or user_check.roles==3:
            delete_user.status = 0
            today = datetime.now()
            date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            delete_user.updated_at = date_time_obj
            db.session.commit()
            app.logger.info(f"{delete_user} disabled successfully")
            return jsonify(status=200, message=f"{delete_user} disabled successfully")
        app.logger.info("User not allowed to perform this action")
        return jsonify(status=404, message="User not allowed to perform this action")
