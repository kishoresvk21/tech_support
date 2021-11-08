from flask import jsonify, request
from sqlalchemy.future import select
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from sqlalchemy.orm import query
from sqlalchemy.sql.expression import delete
from sqlalchemy.sql.functions import user
from werkzeug.security import generate_password_hash, check_password_hash
from app.user.models.models import User, Technologies, Queries, Comments,Opinion
from app import app, db
from sqlalchemy import or_,and_,desc
import re,ast
from app.authentication import encode_auth_token,authentication,is_active
from app.user.serilalizer.serilalizer import query_serializer,comments_serializer, user_serializer,replace_with_ids,technology_serializer
from app.user.pagination.pagination import get_paginated_list
# from utils.smtp_mail import send_mail_to_reset_password


class AdminComment(Resource):
    # @authentication
    def put(self):
        data = request.get_json() or {}
        query_id = data.get('query_id')
        user_id = data.get('user_id')
        comment_id = data.get('comment_id')
        edited_comment = data.get('edited_comment')
        edit_comment_by_id = db.session.query(Comments).filter_by(id=comment_id).first()
        check_user = db.session.query(User).filter_by(id=user_id).first()
        check_query=db.session.query(Queries).filter_by(id=query_id).first()
        check_comment=db.session.query(Comments).filter_by(id=comment_id).first()
        check_queries_auth = db.session.query(Queries).filter_by(u_id=user_id).first()
        if not (query_id and user_id and edited_comment and comment_id):
            app.logger.info("query_id , user_id , edited_comment and comment_id are required fields")
            return jsonify(status=400, message="query_id , user_id , edited_comment and comment_id are required fields")
        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=404,message="user not found")
        if not check_query:
            app.logger.info("query not found")
            return jsonify(status=404,message="query not found")
        if not check_comment:
            app.logger.info("comment not found")
            return jsonify(status=404,message="comment not found")
        if not check_user != 1:
            app.logger.info("cant edit comment")
            return jsonify(status=404, message="cant edit comment")
        active=is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404,message="admin disabled temporarily")
        if not (check_user.roles == 2 or check_user.roles == 3):
            app.logger.info("User not allowed to edit")
            return jsonify(status=404, message="User not allowed to edit")
        edit_comment_by_id.msg = edited_comment
        db.session.commit()
        app.logger.info("Comment edited")
        return jsonify(status=200, message="Comment edited",
                       data={"query_id": query_id, "comment_id": comment_id, "edited_comment": edited_comment})

    # @authentication
    def delete(self):
        data = request.get_json() or {}

        query_id = data.get('query_id')
        user_id = data.get('user_id')
        comment_id = data.get('comment_id')

        if not (query_id and user_id and comment_id):
            app.logger.info("Query_id , user_id and comment_id are required")
            return jsonify(status=200, message="Query_id , user_id and comment_id are required")

        query_check = db.session.query(Queries).filter_by(id=query_id).first()
        user_check = db.session.query(User).filter_by(id=user_id).first()
        comment_check = db.session.query(Comments).filter_by(id=comment_id).first()

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")

        if not query_check:
            app.logger.info("Query not found")
            return jsonify(status=400, message="Query not found")

        if not comment_check:
            app.logger.info("Comment not found")
            return jsonify(status=400, message="Comment not found")

        if not (user_check.roles != 1):
            app.logger.info("User not allowed to delete")
            return jsonify(status=404, message="User not allowed to delete")

        # if user_check.status==False:
        #     app.logger.info("admin disabled temporarily")
        #     return jsonify(status=404,message="admin disabled temporarily")

        delete_likes_dislikes_comment = Opinion.query.filter_by(c_id=comment_id).all()
        for itr in delete_likes_dislikes_comment:
            db.session.delete(itr)
            db.session.commit()
        db.session.delete(comment_check)
        db.session.commit()
        app.logger.info("Comment deleted successfully")
        return jsonify(status=200, message="Comment deleted successfully")

    def get(self):  # send all the comments
        order_by_comment_obj = db.session.query(Comments).order_by(Comments.updated_at)
        if not order_by_comment_obj:
            app.logger.info("No record found")
            return jsonify(status=404, message="No record found")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        c_list = []
        for itr in order_by_comment_obj:
            dt = comments_serializer(itr)
            c_list.append(dt)

        app.logger.info("Return comments data")
        return jsonify(status=200, data=get_paginated_list(c_list, '/admin/comment', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning comments data")


class AdminGetCommentsByUserId(Resource):
    def get(self): #send all the comments based on user_id
        # from_date = request.args.get("from_date")
        user_id= int(request.args.get('user_id'))
        print(user_id)
        c_list = []
        user_obj=db.session.query(User).filter_by(id=user_id).all()
        comments_obj = db.session.query(Comments).filter_by(u_id=user_id).all()

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        if not user_obj:
            app.logger.info("user not found")
            return jsonify(status=404, message="user not found")
        if not comments_obj:
            app.logger.info("No records found")
            return jsonify(status=404, message="No records found")

        for itr in comments_obj:
            if itr.u_id == user_id:
                dt = comments_serializer(itr)
                print(dt)
                c_list.append(dt)

        # if not c_list:
        #     app.logger.info("No records found")
        #     return jsonify(status=404, message="No records found")

        # user_id_str = str(user_id)
        # page = "/admin/commentsbyuserid"+user_id_str
        page = f"/admin/commentsbyuserid?user_id={user_id}"
        # data = get_paginated_list(c_list, page, start=request.args.get('start', 1),
        #                           limit=request.args.get('limit', 3)),

        app.logger.info("Return comments data")
        return jsonify(status=200, data = get_paginated_list(c_list, page, start=request.args.get('start', 1),
                                  limit=request.args.get('limit', 3),with_params=True),message="Returning queries data")
