from flask import request, jsonify
from app import app, db
from datetime import datetime
from flask_restplus import Resource
from app.authentication import authentication
from app.models_package.models import User, Queries, Comments, LikesDislikes
from app.serializer import comments_serializer
from app.pagination import get_paginated_list
from app.authentication import get_user_id, is_active
from app.utils.form_validation import description_validator
from app.utils.file_upload import upload_file


class CommentCRUD(Resource):
    @authentication
    def post(self):
        file = request.files.get('file')
        try:
            user_id = request.form['user_id']
            # comment_id = request.form['comment_id']
            query_id = request.form['query_id']
            user_id = request.form['user_id']
            comment = request.form['comment']
        except:
            app.logger.info("query_id,user_id and comment are required")
            return jsonify(status=400, message="query_id,user_id and comment are required")
        if not (query_id and user_id and comment):
            app.logger.info("query_id,user_id and comment or file are required")
            return jsonify(status=400, message="query_id,user_id and comment or file are required")
        if not is_active(user_id):
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
            file_path = upload_file(self, file)
        else:
            file_path = None
        comm = Comments(user_id, query_id, comment, file_path, today, today)
        db.session.add(comm)
        db.session.commit()
        app.logger.info("comment inserted successfully")
        return jsonify(status=200, message="comment inserted successfully")

    # def post(self):
    #     data = request.get_json() or {}
    #     query_id = request.form['query_id']
    #     user_id = request.form['user_id']
    #     comment = request.form['comment']
    #
    #     if not (query_id and user_id and comment):
    #         app.logger.info("query_id,user_id and comment are required")
    #         return jsonify(status=400, message="query_id,user_id and comment are required")
    #
    #     # file = request.files.getlist('file[]')
    #     # if not file:
    #     #     app.logger.info('file required')
    #     #     return jsonify(status=400, message="file required")
    #
    #     queries_check = Queries.query.filter_by(id=query_id).first()
    #     user_check = db.session.query(User).filter_by(id=user_id).first()
    #
    #     if not description_validator(comment):
    #         app.logger.info("Invalid comment length")
    #         return jsonify(status=400, message="Invalid comment length")
    #     if not user_check:
    #         app.logger.info("user not found")
    #         return jsonify(status=404, message="user not found")
    #     if not queries_check:
    #         app.logger.info("query not found")
    #         return jsonify(status=404, message="query not found")
    #
    #     today = datetime.now()
    #     date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
    #     comm = Comments(user_id, query_id, comment, date_time_obj, date_time_obj)
    #     db.session.add(comm)
    #     db.session.commit()
    #     # comment_id_obj = Comments.query.filter_by(msg=comment).first()
    #     # upload_file(user_id, comment_id_obj, file)
    #
    #     app.logger.info("comment inserted successfully")
    #     return jsonify(status=200, message="comment inserted successfully")


    # def post(self):
    #     data = request.get_json() or {}
    #     query_id = data.get('query_id')
    #     user_id = data.get('user_id')
    #     comment = data.get('comment')
    #     if not (query_id and user_id and comment):
    #         app.logger.info("query_id,user_id and comment are required")
    #         return jsonify(status=400, message="query_id,user_id and comment are required")
    #     queries_check = Queries.query.filter_by(id=query_id).first()
    #     user_check = db.session.query(User).filter_by(id=user_id).first()
    #
    #     if not description_validator(comment):
    #         app.logger.info("Invalid comment length")
    #         return jsonify(status=400, message="Invalid comment length")
    #
    #     if not user_check:
    #         app.logger.info("user not found")
    #         return jsonify(status=404, message="user not found")
    #     if not queries_check:
    #         app.logger.info("query not found")
    #         return jsonify(status=404, message="query not found")
    #     today = datetime.now()
    #     date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
    #     comm = Comments(user_id, query_id, comment, date_time_obj, date_time_obj)
    #     db.session.add(comm)
    #     db.session.commit()
    #     app.logger.info("comment inserted successfully")
    #     return jsonify(status=200, message="comment inserted successfully")

    @authentication
    def put(self):
        try:
            user_id = request.form['user_id']
            query_id = request.form['query_id']
            comment_id = request.form['comment_id']
            edited_comment = request.form['edited_comment']
        except:
            app.logger.info("user_id,query_id,comment_id and edited_comment are required")
            return jsonify(status=400, message="user_id,query_id,comment_id and edited_comment are required")

        new_file = request.files.get('file')

        edit_comment_by_id = db.session.query(Comments).filter_by(id=comment_id).first()
        check_user = db.session.query(User).filter_by(id=user_id).first()
        check_queries_auth = db.session.query(Queries).filter_by(u_id=user_id).first()

        if not description_validator(edited_comment):
            app.logger.info("Invalid comment length")
            return jsonify(status=400, message="Invalid comment length")

        if not (check_queries_auth or check_user != 1):
            app.logger.info("cant edit comment")
            return jsonify(status=404, message="cant edit comment")

        if not edit_comment_by_id:
            app.logger.info("Comment not found")
            return jsonify(status=400, message="Comment not found")

        if not ((edit_comment_by_id.u_id != user_id) or check_user.roles != 1):
            app.logger.info("User not allowed to edit")
            return jsonify(status=404, message="User not allowed to edit")

        edit_comment_by_id.msg = edited_comment
        if new_file:
            file_data = upload_file(self, new_file)
            new_file_name = file_data
            # new_file_path = file_data[1]
        else:
            new_file_name = None
            # new_file_path = None
        edit_comment_by_id.file_path = new_file_name
        # edit_comment_by_id.filepath = new_file_path
        db.session.commit()
        app.logger.info("Comment edited")
        return jsonify(status=200, message="Comment edited",
                       data={"query_id": query_id, "comment_id": comment_id, "edited_comment": edited_comment})

    # def put(self):
    #     data = request.get_json() or {}
    #     if not data:
    #         app.logger.info("No input(s)")
    #         return jsonify(status=400, message="No input(s)")
    #     try:
    #         query_id = data.get('query_id')
    #         user_id = data.get('user_id')
    #         comment_id = data.get('comment_id')
    #         edit_comment_by_id = db.session.query(Comments).filter_by(id=comment_id).first()
    #         check_user = db.session.query(User).filter_by(id=user_id).first()
    #         check_queries_auth = db.session.query(Queries).filter_by(u_id=user_id).first()
    #     except:
    #         app.logger.info("comment/user/query not found")
    #         return jsonify("comment/user/query not found")
    #
    #     edited_comment = data.get('edited_comment')
    #     if not (query_id and user_id and edited_comment and comment_id):
    #         app.logger.info("query_id , user_id , edited_comment and comment_id are required fields")
    #         return jsonify(status=400, message="query_id , user_id , edited_comment and comment_id are required fields")
    #
    #     if not description_validator(edited_comment):
    #         app.logger.info("Invalid comment length")
    #         return jsonify(status=400, message="Invalid comment length")
    #
    #     if not (check_queries_auth or check_user != 1):
    #         app.logger.info("cant edit comment")
    #         return jsonify(status=404, message="cant edit comment")
    #
    #     if not edit_comment_by_id:
    #         app.logger.info("Comment not found")
    #         return jsonify(status=400, message="Comment not found")
    #
    #     if not ((edit_comment_by_id.u_id == user_id) or check_user.role != 1):
    #         app.logger.info("User not allowed to edit")
    #         return jsonify(status=404, message="User not allowed to edit")
    #
    #     edit_comment_by_id.msg = edited_comment
    #     db.session.commit()
    #     app.logger.info("Comment edited")
    #     return jsonify(status=200, message="Comment edited",
    #                    data={"query_id": query_id, "comment_id": comment_id, "edited_comment": edited_comment})

    # @authentication

    def delete(self):
        data = request.get_json() or {}
        query_id = data.get('query_id')
        user_id = data.get('user_id')
        comment_id = data.get('comment_id')
        if not (query_id and user_id and comment_id):
            app.logger.info("comment_id , user_id and query_id are required")
            return jsonify(status=200, message="Query_id , user_id and query_id are required")
        query_check = Queries.query.filter_by(id=query_id).first()
        user_check = User.query.filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")

        if not query_check:
            app.logger.info("Query not found")
            return jsonify(status=400, message="Query not found")
        comment_check = Comments.query.filter_by(id=comment_id).first()
        if not comment_check:
            app.logger.info("Comment not found")
            return jsonify(status=400, message="Comment not found")
        if not ((comment_check.u_id == user_id) or user_check.roles != 1):
            app.logger.info("User not allowed to delete")
            return jsonify(status=404, message="User not allowed to delete")

        delete_likes_dislikes_comment = LikesDislikes.query.filter_by(c_id=comment_id).all()
        for itr in delete_likes_dislikes_comment:
            db.session.delete(itr)
            db.session.commit()
        db.session.delete(comment_check)
        db.session.commit()
        app.logger.info("Comment deleted successfully")
        return jsonify(status=200, message="Comment deleted successfully")

    def get(self):  # send all the comments based on comment_id or u_id or q_id or send all
        order_by_comment_obj = db.session.query(Comments).order_by(Comments.updated_at)
        if not order_by_comment_obj:
            app.logger.info("No Comments in DB")
            return jsonify(status=404, message="No comments in DB")

        c_list = []
        for itr in order_by_comment_obj:
            user_name = User.query.filter_by(id=itr.u_id).first()
            dt = comments_serializer(itr,itr.u_id)
            dt['name'] = user_name.name
            c_list.append(dt)

        app.logger.info("Return comments data")
        return jsonify(status=200, data=get_paginated_list(c_list, '/comment', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning comments data")


class GetCommentByQuery(Resource):
    @authentication
    def get(self):
        user_id=get_user_id(self)
        query_id=request.args.get('query_id')
        comment_obj = Comments.query.filter_by(q_id=query_id).all()
        if not comment_obj:
            app.logger.info("No Comments found")
            return jsonify(status=404, message="No comments found")
        comment_list = []
        page = f"/getcomments/query?query_id={query_id}"
        for itr in comment_obj:
            dt = comments_serializer(itr, int(user_id))
            comment_list.append(dt)
        app.logger.info("Return comments data")
        return jsonify(status=200, data=get_paginated_list(comment_list, page,start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=True),message="Returning queries data")


#My Contributions


class GetCommentsByUserId(Resource):
    def get(self, user_id):  # send all the comments based on user_id
        try:
            c_list = []
            comments_obj = Comments.query.filter_by(u_id=user_id).all()

            if not comments_obj:
                app.logger.info("No Comments in DB")
                return jsonify(status=404, message="No comments in DB")

            for itr in comments_obj:
                if itr.u_id == user_id:
                    dt = comments_serializer(itr,itr.u_id)
                    c_list.append(dt)
            user_id_str = str(user_id)
            page = '/getcomments/user/' + user_id_str

            app.logger.info("Return comments data")
            return jsonify(status=200, data=get_paginated_list(c_list, page, start=request.args.get('start', 1),
                                                               limit=request.args.get('limit', 3),with_params=False),
                           message="Returning comments data")
        except:
            return jsonify(status=400, message="No inputs found")


