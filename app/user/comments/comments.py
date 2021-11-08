from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments,Opinion
from app import app, db
from sqlalchemy import or_, and_, desc
import re, ast
from app.authentication import encode_auth_token, authentication,get_user_id,is_active
from app.user.serilalizer.serilalizer import comments_serializer,replace_with_ids
from app.user.pagination.pagination import get_paginated_list
from app.user.fileupload.file_upload import upload_file
from app.utils.form_validations import description_validator

class UserComment(Resource):
    # @authentication
    def post(self):
        file = request.files.get('file')
        # if not file:
        #     app.logger.info("file is required")
        #     return jsonify(status=400, message="file is required")
        try:
            query_id = request.form['query_id']
            user_id = request.form['user_id']
            comment = request.form['comment']
        except:
            app.logger.info("query_id,user_id and comment are required")
            return jsonify(status=400, message="query_id,user_id and comment are required")
        active=is_active(user_id)
        if not active:
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, message="User is temporarily disabled")
        queries_check = Queries.query.filter_by(id=query_id).first()
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=404, message="user not found")
        if not queries_check:
            app.logger.info("query not found")
            return jsonify(status=404, message="query not found")
        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        if file:
            file = upload_file(self, file)
            file_name=file[0]
            file_path=file[1]
            print(file_path)
        else:
            file_path = None
        comm = Comments(user_id, query_id,comment,file_name,file_path,date_time_obj,date_time_obj)
        db.session.add(comm)
        db.session.commit()
        app.logger.info("comment inserterd succesfully")
        return jsonify(status=200, message="comment inserterd succesfully")

    # def post(self):
    #     user_id = get_user_id(self)
    #     data = request.get_json() or {}
    #     query_id = data.get('query_id')
    #     # file = request.files.getlist('file[]')
    #     queries_check = db.session.query(Queries).filter_by(id=query_id).first()
    #     user_check = db.session.query(User).filter_by(id=user_id).first()
    #     comment = data.get('comment')
    #     if not (query_id and comment):
    #         app.logger.info("query_id and comment are required")
    #         return jsonify(status=400, message="query_id and comment are required")
    #     active = is_active(user_id)
    #     if not active:
    #         app.logger.info("user disabled temporarily")
    #         return jsonify(status=400, message="user disabled temporarily")
    #     if not user_check:
    #         app.logger.info("user not found")
    #         return jsonify(status=400, message="user not found")
    #     if not queries_check:
    #         app.logger.info("query not found")
    #         return jsonify(status=400, message="query not found")
    #
    #     comment_check = description_validator(comment)
    #     if not comment_check:
    #         app.logger.info("Invalid comment")
    #         return jsonify(status=200, message="Invalid comment")
    #
    #     today = datetime.now()
    #     date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
    #     comm = Comments(user_id, query_id, comment, date_time_obj, date_time_obj)
    #     db.session.add(comm)
    #     db.session.commit()
    #     app.logger.info("comment inserterd succesfully")
    #     return jsonify(status=200, message="comment inserterd succesfully")

    # @authentication
    def put(self):
      try:
        user_id = request.form['user_id']
        comment_id = request.form['comment_id']
        edited_comment = request.form['edited_comment']
      except:
          app.logger.info("user_id,comment_id and edited_comment are required")
          return jsonify(status=400,message="user_id,comment_id and edited_comment are required")
      new_file = request.files.get('file')
      edit_comment_by_id = db.session.query(Comments).filter_by(id=comment_id).first()
      check_user = db.session.query(User).filter_by(id=user_id).first()
      check_queries_auth = db.session.query(Comments).filter_by(u_id=user_id).first()
      # edited_comment = request.form['edited_comment']
      # if not (query_id and edited_comment and comment_id):
      #       app.logger.info("query_id ,edited_comment and comment_id are required fields")
      #       return jsonify(status=400, message="query_id , edited_comment and comment_id are required fields")
      active = is_active(user_id)
      if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
      if not check_user:
            app.logger.info("user not found")
            return jsonify(status=404, message="user not found")
      if not (check_queries_auth or check_user != 1):
            app.logger.info("cant edit comment")
            return jsonify(status=404, message="cant edit comment")
      if not edit_comment_by_id:
            app.logger.info("Comment not found")
            return jsonify(status=400, message="Comment not found")
      if not ((edit_comment_by_id.u_id == user_id) or check_user.roles != 1):
            app.logger.info("User not allowed to edit")
            return jsonify(status=404, message="User not allowed to edit")

      description_check = description_validator(edited_comment)
      if not description_check:
            app.logger.info("Invalid comment")
            return jsonify(status=200, message="Invalid comment")
      edit_comment_by_id.msg = edited_comment
      if new_file:
          file_data = upload_file(self,new_file)
          new_file_name = file_data[0]
          new_file_path = file_data[1]
      else:
          new_file_name=None
          new_file_path = None
      edit_comment_by_id.filename=new_file_name
      edit_comment_by_id.filepath=new_file_path
      db.session.commit()
      app.logger.info("Comment edited")
      return jsonify(status=200, message="Comment edited",
                       data={"comment_id": comment_id, "edited_comment": edited_comment})
        # user_id = get_user_id(self)
        # data = request.get_json() or {}
        # query_id = data.get('query_id')
        # comment_id = data.get('comment_id')
        # query_check=db.session.query(Queries).filter_by(id=query_id).first()
        # edit_comment_by_id = db.session.query(Comments).filter_by(id=comment_id).first()
        # check_user = db.session.query(User).filter_by(id=user_id).first()
        # check_queries_auth = db.session.query(Queries).filter_by(u_id=user_id).first()
        # edited_comment = data.get('edited_comment')
        # if not (query_id and edited_comment and comment_id):
        #     app.logger.info("query_id ,edited_comment and comment_id are required fields")
        #     return jsonify(status=400, message="query_id , edited_comment and comment_id are required fields")
        # active = is_active(user_id)
        # if not active:
        #     app.logger.info("user disabled temporarily")
        #     return jsonify(status=400, message="user disabled temporarily")
        # if not check_user:
        #     app.logger.info("user not found")
        #     return jsonify(status=404, message="user not found")
        # if not query_check:
        #     app.logger.info("query not found")
        #     return jsonify(status=404, message="query not found")
        # if not (check_queries_auth or check_user != 1):
        #     app.logger.info("cant edit comment")
        #     return jsonify(status=404, message="cant edit comment")
        # if not edit_comment_by_id:
        #     app.logger.info("Comment not found")
        #     return jsonify(status=400, message="Comment not found")
        # if not ((edit_comment_by_id.u_id == user_id) or check_user.roles != 1):
        #     app.logger.info("User not allowed to edit")
        #     return jsonify(status=404, message="User not allowed to edit")
        #
        # comment_check = description_validator(edited_comment)
        # if not comment_check:
        #     app.logger.info("Invalid comment")
        #     return jsonify(status=200, message="Invalid comment")
        #
        # edit_comment_by_id.msg = edited_comment
        # db.session.commit()
        # app.logger.info("Comment edited")
        # return jsonify(status=200, message="Comment edited",
        #                data={"query_id": query_id, "comment_id": comment_id, "edited_comment": edited_comment})

    @authentication
    def delete(self):
        user_id = get_user_id(self)
        data = request.get_json() or {}
        query_id = data.get('query_id')
        comment_id = data.get('comment_id')
        if not (query_id and comment_id):
            app.logger.info("Query_id and comment_id are required")
            return jsonify(status=200, message="Query_id and comment_id are required")
        query_check = db.session.query(Queries).filter_by(id=query_id).first()
        user_check = db.session.query(User).filter_by(id=user_id).first()

        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        if not query_check:
            app.logger.info("Query not found")
            return jsonify(status=400, message="Query not found")
        comment_check = db.session.query(Comments).filter_by(id=comment_id).first()
        if not comment_check:
            app.logger.info("Comment not found")
            return jsonify(status=400, message="Comment not found")
        if not ((comment_check.u_id == user_id) or user_check.roles != 1):
            delete_likes_dislikes=Opinion.query.filter_by(q_id=query_id).all()
            if delete_likes_dislikes:
                for itr in delete_likes_dislikes:
                  db.session.delete(itr)
                  db.session.commit()
            else:
                app.logger.info("No likes or dislikes for this comment, deleting this comment ")
            db.session.delete(comment_check)
            db.session.commit()
            app.logger.info("Comment deleted successfully")
            return jsonify(status=200, message="Comment deleted successfully")
        app.logger.info("User not allowed to delete")
        return jsonify(status=404, message="User not allowed to delete")

    def get(self):  # send all the comments based on comment_id or u_id or q_id or send all

        user_id=get_user_id(self)
        order_by_comment_obj = db.session.query(Comments).order_by(Comments.updated_at)
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        if not order_by_comment_obj:
            app.logger.info("No records found")
            return jsonify(status=404, message="No records found")
        c_list = []
        for itr in order_by_comment_obj:
            dt = comments_serializer(itr,user_id)
            c_list.append(dt)

        app.logger.info("Return comments data")
        return jsonify(status=200, data=get_paginated_list(c_list, '/comment', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3)),
                       message="Returning comments data")

class UserGetCommentByQueryId(Resource):
    def get(self):

        user_id=get_user_id(self)
        query_id=request.args.get('query_id')
        if not query_id:
            app.logger.info("query_id required")
            return jsonify(status=404, message="query_id required")
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        comment_obj = db.session.query(Comments).filter_by(id=query_id).all()
        if not comment_obj:
            app.logger.info("No Comments found")
            return jsonify(status=404, message="No comments found")
        comment_list = []
        for itr in comment_obj:
            dt = comments_serializer(itr,user_id)
            comment_list.append(dt)
        page=f'/user/user/getcommentsbyqueryid?query_id={query_id}'
        app.logger.info("Return comments data")
        return jsonify(status=200,
                       data=get_paginated_list(comment_list,page,start=request.args.get('start', 1),
                                               limit=request.args.get('limit', 3),with_params=True), message="Returning queries data")


class UserGetCommentsByuserId(Resource):

    def get(self):  # send all the comments based on user_id
        user_id = request.args.get('user_id')
        if not user_id:
            app.logger.info('user_id required')
            return jsonify(status=400,message="user_id required")
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        try:
            c_list = []
            comments_obj = db.session.query(Comments).filter_by(u_id=user_id).first()
            user_obj=db.session.query(User).filter_by(id=user_id).first()

            if not user_obj:
                app.logger.info("user not found")
                return jsonify(status=404,message="user not found")
            if not comments_obj:
                app.logger.info("No records found")
                return jsonify(status=404, message="No records found")

            for itr in comments_obj:
                if itr.u_id == user_id:
                    dt = comments_serializer(itr,user_id)
                    c_list.append(dt)

            if not c_list:
                app.logger.info("No records found")
                return jsonify(status=404, message="No records found")

            page = f'/user/getcommentsbyuserid?user_id=f{user_id}'

            app.logger.info("Return comments data")
            return jsonify(status=200, data=get_paginated_list(c_list, page, start=request.args.get('start', 1),
                                                               limit=request.args.get('limit', 3),with_params=True),
                           message="Returning queries data")

        except:
            return jsonify(status=400, message="No inputs found")


# class GetCommentsByUserId(Resource):
#
#     def get(self, user_id):  # send all the comments based on user_id
#         try:
#             c_list = []
#             comments_obj = db.session.query(Comments).filter_by(u_id=user_id).all()
#
#             if not comments_obj:
#                 app.logger.info("No Comments in DB")
#                 return jsonify(status=404, message="No comments in DB")
#
#             for itr in comments_obj:
#                 if itr.u_id == user_id:
#                     dt = comments_serializer(itr)
#                     c_list.append(dt)
#
#             user_id_str = str(user_id)
#             page = '/getcomments/user/' + user_id_str
#
#             app.logger.info("Return comments data")
#             return jsonify(status=200, data=get_paginated_list(c_list, page, start=request.args.get('start', 1),
#                                                                limit=request.args.get('limit', 3)),
#                            message="Returning queries data")
#
#         except:
#             return jsonify(status=400, message="No inputs found")

