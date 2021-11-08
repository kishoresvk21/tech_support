from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments
from app import app, db
from sqlalchemy import or_, and_, desc
import re, ast
from app.authentication import encode_auth_token, authentication,is_active
from app.user.serilalizer.serilalizer import user_serializer
from app.user.pagination.pagination import get_paginated_list

class getusers(Resource):
    def get(self):

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        users_list = []
        user = User.query.filter(User.roles == 1).all()

        if not user:
            app.logger.info("No user found")
            return jsonify(status=400, message="No user found")
        for itr in user:
            dt = user_serializer(itr)
            users_list.append(dt)
            print(users_list)
        return jsonify(status=200,
                       data=get_paginated_list(users_list, '/getusers', start=request.args.get('start', 1),
                                               limit=request.args.get('limit', 3)),
                       message="Returning all  user's name and ids")

class UserSearch(Resource):
    def get(self):
        name=request.args.get('name')
        if not name:
            app.logger.info('name required')
            return jsonify(status=400,message="name required")
        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")
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
            data=get_paginated_list(user_list, page, start=request.args.get('start', 1),
            limit=request.args.get('limit', 3),with_params=False), message="Returning user data")

