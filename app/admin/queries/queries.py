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
from app.authentication import encode_auth_token,authentication,is_active
from app.user.serilalizer.serilalizer import query_serializer,comments_serializer, user_serializer,replace_with_ids,technology_serializer
from app.user.pagination.pagination import get_paginated_list
# from utils.smtp_mail import send_mail_to_reset_password

class AdminQueries(Resource):
    def put(self):
        data = request.get_json() or {}
        query_id = data.get('query_id')
        user_id = data.get('user_id')
        tech = data.get('technology')
        title = data.get('title')
        description = data.get('description')
        user_check = db.session.query(User).filter_by(id=user_id).first()
        tech_check = db.session.query(Technologies).filter_by(name=tech).first()
        query_check = db.session.query(Queries).filter_by(id=query_id).first()

        if not (query_id and user_id and title and description and tech):
            app.logger.info("Query id , User id , title , description, technology are required fields")
            return jsonify(status=400,
                           message="Query id , User id , title , description, technology are required fields")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        if not query_check:
            app.logger.info("query not found")
            return jsonify(status=400, message="query not found")
        if not tech_check:
            app.logger.info("techology not found")
            return jsonify(status=400,message="technology not found")


    # @authentication
    def delete(self):
        data = request.get_json() or {}
        query_id = data.get('query_id')
        user_id = data.get('user_id')
        query_check = db.session.query(Queries).filter_by(id=query_id).first()
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not (query_id and user_id):
            app.logger.info("query_id and user_id are required")
            return jsonify(status=404, message="query_id and user_id are required")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=404, message="user not found")
        if not query_check:
            app.logger.info("Query not found")
            return jsonify(status=404, message="Query not found")
        if query_check:
            if user_check.roles != 1: # admin or super admin can delete
                delete_comment = db.session.query(Comments).filter_by(q_id=query_id).all()
                if delete_comment:
                    for itr in delete_comment:
                        delete_likes_dislikes_comment = Opinion.query.filter_by(c_id=itr.id).all()
                        for itr2 in delete_likes_dislikes_comment:
                            db.session.delete(itr2)
                            db.session.commit()
                        db.session.delete(itr)
                        db.session.commit()
                else:
                    app.logger.info("No comments for this query, deleting this query ")
                db.session.delete(query_check)
                db.session.commit()
                app.logger.info("Query deleted successfully")
                return jsonify(status=200, message="Query deleted successfully")
            app.logger.info("User not allowed to delete")
            return jsonify(status=404, message="User not allowed to delete")

        app.logger.info("Query not found")
        return jsonify(status=400, message="Query not found")

    def get(self):  # send all the queries
        order_by_query_obj = db.session.query(Queries).order_by(Queries.updated_at)
        if not order_by_query_obj:
            app.logger.info("No records found")
            return jsonify(status=404, message="No records found")

        c_list = []
        for itr in order_by_query_obj:
            dt = query_serializer(itr)
            c_list.append(dt)

        app.logger.info("Return queries data")
        return jsonify(status=200, data=get_paginated_list(c_list, '/admin/query', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3)),
                       message="Returning queries data")


class AdminGetQueryByUserId(Resource):
    def get(self):
        user_id=request.args.get('user_id')
        if not user_id:
            app.logger.info("user_id required")
            return jsonify(status=400,message="user_id required")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        queries_obj = db.session.query(Queries).filter_by(u_id=user_id).all()
        if not queries_obj:
            app.logger.info("No records found")
            return jsonify(status=404, message="No records found")
        queries_list=[]
        for itr in queries_obj:
            dt = query_serializer(itr)
            queries_list.append(dt)
        page = f'/admin/getquerybyuserid?user_id={user_id}'
        app.logger.info("Returning queries data")
        return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
                                          limit=request.args.get('limit', 3)), message="Returning queries data")

class Unanswered(Resource):
    def get(self):

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        unanswered_queries_obj_list = []
        unanswered_queries_list = []

        r = db.session.query(Queries, Comments).outerjoin(Comments, Queries.id == Comments.q_id).all()
        if not r:
            app.logger.info("no records found")
            return jsonify(status=404, message="no records found")

        for result in r:
            if not result[1]:
                unanswered_queries_obj_list.append(result[0])

        # print(unanswered_queries_obj_list)
        if not unanswered_queries_obj_list:
            app.logger.info("no records found")
            return jsonify(status=404, message="no records found")

        for itr in unanswered_queries_obj_list:
            dt = query_serializer(itr)
            unanswered_queries_list.append(dt)

        app.logger.info("Returning queries data")
        return jsonify(status=200,data=get_paginated_list(unanswered_queries_list, '/unanswered', start=request.args.get('start', 1),
                                          limit=request.args.get('limit', 3)),message="Returning unanswered queries data")

