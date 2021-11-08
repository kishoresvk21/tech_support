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


class Technology(Resource):
    @authentication
    def post(self):
        data = request.get_json() or {}
        user_id = data.get('user_id')
        technologies = data.get('technologies')
        if not (user_id and technologies):
            app.logger.info("User_id and technologies are required")
            return jsonify(status=404, message="User_id and technologies are required")
        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")
        check_user = User.query.filter_by(id=user_id).first()
        if not check_user:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        if not (check_user.roles == 2 or check_user.roles == 3):
            app.logger.info("User not allowed to add technologies")
            return jsonify(status=404, message="User not allowed to add technologies")
        for itr in technologies:
            check_tech_exist = Technologies.query.filter_by(name=itr).first()
            if check_tech_exist:
                app.logger.info(f"{itr} technology already exists")
                return jsonify(status=400, message=f"{itr} technology already exists")
        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        for itr in technologies:
            tech = Technologies(itr, date_time_obj, date_time_obj)
            db.session.add(tech)
            db.session.commit()
        return jsonify(status=200, message="added successfully")

    def put(self):
        data = request.get_json() or {}
        user_id = data.get('user_id')
        tech_id = data.get('technology_id')
        technology_name = data.get('technology_name')
        if not (user_id and tech_id and technology_name):
            app.logger.info("User_id, technology_id and technology_name are required")
            return jsonify(status=404, message="User_id, technology_id and technology_name are required")
        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")
        check_user = User.query.filter_by(id=user_id).first()
        check_tech = Technologies.query.filter_by(id=tech_id).first()

        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if not check_tech:
            app.logger.info("Technology not found")
            return jsonify(status=400, message="Technology not found")

        if not (check_user.roles == 2 or check_user.roles == 3):
            app.logger.info("User not allowed to add technologies")
            return jsonify(status=404, message="User not allowed to add technologies")

        if check_tech and check_tech.status == 0:
            app.logger.info(f"{check_tech.name} technology does not exists")
            return jsonify(status=400, message=f"{check_tech.name} technology does not exists")

        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')

        check_tech.name = technology_name
        check_tech.updated_at = date_time_obj
        db.session.commit()
        return jsonify(status=200, message="added successfully")

    def get(self):

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        t_list = []
        technology_obj = db.session.query(Technologies).order_by(Technologies.updated_at)

        if not technology_obj:
            app.logger.info("No Technologies in DB")
            return jsonify(status=404, message="No Technologies in DB")

        for itr in technology_obj:
            if itr.status==True:
             dt = technology_serializer(itr)
             t_list.append(dt)

        if not t_list:
            app.logger.info("No Technologies in DB")
            return jsonify(status=404, message="No Technologies in DB")

        app.logger.info("Return Technologies data")
        return jsonify(status=200, data=t_list, message="Returning Technologies data")

    @authentication
    def delete(self):
        data = request.get_json() or {}
        technology = data.get('technology')
        user_id = data.get('user_id')
        tech_check = db.session.query(Technologies).filter_by(name=technology).first()
        user_check = db.session.query(User).filter_by(id=user_id).first()

        if not (technology and user_id):
            app.logger.info("technology, user_id required to delete")
            return jsonify(status=404, message="technology, user_id required to delete")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        if tech_check:
            if (user_check.roles == 2 or user_check.roles == 3):
                db.session.delete(tech_check)
                db.session.commit()
                app.logger.info("Technology deleted successfully")
                return jsonify(status=200, message="Technology deleted successfully")
            app.logger.info("User not allowed to delete")
            return jsonify(status=404, message="User not allowed to delete")

        app.logger.info("Technology not found")
        return jsonify(status=400, message="Technology not found")

