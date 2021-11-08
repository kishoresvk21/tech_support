from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments
from app import app, db
from sqlalchemy import or_, and_, desc,func
import re, ast
from app.authentication import encode_auth_token, authentication,is_active
from app.user.serilalizer.serilalizer import comments_serializer,replace_with_ids
from app.user.pagination.pagination import get_paginated_list
from app.utils.count import update_like_dislike_count


class TopUsers(Resource):
    def get(self):  # send all the comments based on user_id
        update_like_dislike_count(self)
        users_limit=request.args.get('users_limit')
        if not users_limit:
            app.logger.info("users limit required")
            return jsonify(status=400,message="users limit required")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        top_users_list = []
        comments_obj=db.session.query(Comments.u_id,User.name,func.count(Comments.like_count),
                                      func.count(Comments.dislike_count)).\
            group_by(Comments.u_id).order_by((func.count(Comments.like_count)).desc()).outerjoin(User)\
            .all()

        if not comments_obj:
            app.logger.info("No comments in db")
            return jsonify(status=400, message="No comments in db")
        for itr in comments_obj:
            users_data={
                "user_id":itr[0],
                "name":itr[1]
            }

            top_users_list.append(users_data)
        print(top_users_list)
        app.logger.info(f"Return top {users_limit} user data")

        page = "/admin/topusers?users_limit=" + f'{users_limit}'

        return jsonify(status=200, data=get_paginated_list(top_users_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 10), with_params=False),
                       message=f"Returning top {users_limit} users data")


# class topusers(Resource):
#   def get(self):
#      update_like_dislike_count(self)
#      top_ten_list = []
#      top_ten_users_list = []
#      count = 0
#
#      comment_obj_list = Comments.query.filter(Comments.like_count >= Comments.dislike_count). \
#         order_by(Comments.like_count.desc()).all()
#
#      if not comment_obj_list:
#         app.logger.info("No comments in db")
#         return jsonify(status=400, message="No comments in db")
#
#      for itr in comment_obj_list:
#         if itr.like_count and count < 10:
#             # print("cmt_id=", itr.id, "Like count = ", itr.like_count, "dislike count =", itr.dislike_count)
#             user_obj = User.query.filter_by(id=itr.u_id).first()
#             if not user_obj:
#                 app.logger.info("No user in db")
#                 return jsonify(status=400, message="No user in db")
#             top_ten_users_list.append(user_obj)
#             count = count + 1
#
#      for itr in top_ten_users_list:
#         dt = user_serializer(itr)
#         top_ten_list.append(dt)
#      app.logger.info("Return top 10 user data")
#      print(top_ten_list)
#      return jsonify(status=200, data=get_paginated_list(top_ten_list, "/toptenusers", start=request.args.get('start', 1),
#                                                        limit=request.args.get('limit', 3)),
#                    message="Returning top 10 use data")