from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments,SavedQueries,Opinion
from app import app, db
from sqlalchemy import or_, and_, desc
import re, ast
from app.authentication import encode_auth_token, authentication,get_user_id,is_active
from app.user.serilalizer.serilalizer import query_serializer,replace_with_ids,saved_query_serializer
from app.user.pagination.pagination import get_paginated_list
from app.utils.form_validations import title_validator,description_validator
from app.user.fileupload.file_upload import upload_file

class UserQueries(Resource):
    # @authentication
    def post(self):
        file = request.files.get('file')
        try:
            title = request.form['title']
            user_id = request.form['user_id']
            description = request.form['description']
            tech = request.form['technology']
        except:
            app.logger.info("title, description, user_id and technology are required")
            return jsonify(status=400, message="title, description, user_id and technology are required")
        # active=is_active(user_id)
        # if not active:
        #     app.logger.info("User is temporarily disabled")
        #     return jsonify(status=404, message="User is temporarily disabled")
        if not title_validator(title):
            app.logger.info("Invalid title length")
            return jsonify(status=400, message="Invalid title length")
        if not description_validator(description):
            app.logger.info("Invalid description length")
            return jsonify(status=400, message="Invalid description length")
        user_check = User.query.filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        tech_check = Technologies.query.filter_by(name=tech).first()
        if not tech_check:
            app.logger.info("technology not found")
            return jsonify(status=400, message="technology not found")
        query_insertion = Queries.query.filter(or_(Queries.title == title,
                                                   Queries.description == description)).all()
        if query_insertion:
          for itr in query_insertion:
            if itr.title == title:
                app.logger.info("Data already exist")
                return jsonify(status=400, message="Data already exist")
        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        if file:
                file_data = upload_file(self,file)
                filename =file_data[0]
                filepath =file_data[1]
        else:
                filepath = None
                filename = None
        print(filename,filepath)
        question = Queries(user_id,title,description,tech_check.id,filename,filepath, date_time_obj, date_time_obj)
        db.session.add(question)

        db.session.commit()
        # except:
        #     app.logger.info("user not found")
        #     return jsonify(status=400, message="user not found")
        app.logger.info("Query inserted successfully")
        response = query_serializer(question)
        return jsonify(status=200, data=response, message="Query inserted successfully")
        # data = request.get_json() or {}
        # user_id = get_user_id(self)
        # user_check = db.session.query(User).filter_by(id=user_id).first()
        # tech = data.get('technology')
        # tech_check = db.session.query(Technologies).filter_by(name=tech).first()
        # title = data.get('title')
        # description = data.get('description')
        #
        # if not (title and description and tech):
        #     app.logger.info("title, description and technology are required")
        #     return jsonify(status=200, message="title, description and technology are required")
        # active = is_active(user_id)
        # if not active:
        #     app.logger.info("user disabled temporarily")
        #     return jsonify(status=400, message="user disabled temporarily")
        # if not user_check:
        #     app.logger.info("user not found")
        #     return jsonify(status=400, message="user not found")
        # if not tech_check:
        #     app.logger.info("technology not found")
        #     return jsonify(status=400, message="technology not found")
        #
        # query_insertion = db.session.query(Queries).filter(or_(Queries.title == title,
        #                                                        Queries.description == description)).first()
        #
        # if query_insertion:
        #     if query_insertion.title == title:
        #         app.logger.info("Data already exist")
        #         return jsonify(status=200, message="Data already exist")
        #
        # title_check=title_validator(title)
        # if not title_check:
        #     app.logger.info("Invalid title")
        #     return jsonify(status=200, message="Invalid title")
        #
        # description_check=description_validator(description)
        # if not description_check:
        #     app.logger.info("Invalid description")
        #     return jsonify(status=200, message="Invalid description")
        #
        # today = datetime.now()
        # date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        # try:
        #     question = Queries(user_id, title, description, tech_check.id, date_time_obj, date_time_obj)
        #     db.session.add(question)
        #     db.session.commit()
        # except:
        #     app.logger.info("user not found")
        #     return jsonify(status=400, message="user not found")
        # app.logger.info("Query inserted successfully")
        # response = query_serializer(question)
        # return jsonify(status=200, data=response, message="Query inserted successfully")

    # @authentication
    def put(self):
        try:
            user_id = request.form['user_id']
            query_id = request.form['query_id']
            edited_query = request.form['edited_query']
            technology=request.form['technology']
            description=request.form['description']
        except:
            app.logger.info("user_id,query_id,technology,description and edited_query are required")
            return jsonify(status=400, message="user_id,query_id,technology,description and edited_query are required")
        new_file = request.files.get('file')
        query_check = db.session.query(Queries).filter_by(id=query_id).first()
        check_user = db.session.query(User).filter_by(id=user_id).first()
        tech_check = db.session.query(Technologies).filter_by(name=technology).first()
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
        if not query_check:
            app.logger.info("query not found")
            return jsonify(status=400, message="query not found")
        if not tech_check:
            app.logger.info("technology not found")
            return jsonify(status=400, message="technology not found")
        if not ((query_check.u_id == user_id) or check_user.roles != 1):
            app.logger.info("User not allowed to edit")
            return jsonify(status=404, message="User not allowed to edit")

        title_check = title_validator(edited_query)
        if not title_check:
            app.logger.info("Invalid query")
            return jsonify(status=200, message="Invalid query")
        description_check=description_validator(description)
        if not description_check:
            app.logger.info("Invalid description")
            return jsonify(status=200, message="Invalid description")
        query_check.title= edited_query
        query_check.description=description
        query_check.t_id=tech_check.id
        if new_file:
            file_data = upload_file(self, new_file)
            new_file_name = file_data[0]
            new_file_path = file_data[1]
        else:
            new_file_name = None
            new_file_path = None
        query_check.filename = new_file_name
        query_check.filepath = new_file_path
        db.session.commit()
        app.logger.info("Comment edited")
        return jsonify(status=200, message="Comment edited",
                       data={"query_id": query_id, "edited_query": edited_query})
        # data = request.get_json() or {}
        # query_id = data.get('query_id')
        # user_id = get_user_id(self)
        # user_check = db.session.query(Usser).filter_by(id=user_id).first()
        # tech = data.get('technology')
        # tech_check = db.session.query(Technologies).filter_by(name=tech).first()
        # query_check = db.session.query(Queries).filter_by(id=query_id).first()
        # title = data.get('title')
        # description = data.get('description')
        #
        # if not (query_id  and title and description and tech):
        #     app.logger.info("Query id title , description, technology are required fields")
        #     return jsonify(status=404,
        #                    message="Query id, title , description, technology are required fields")
        # active = is_active(user_id)
        # if not active:
        #     app.logger.info("user disabled temporarily")
        #     return jsonify(status=400, message="user disabled temporarily")
        # if not user_check:
        #     app.logger.info("User not found")
        #     return jsonify(status=400, message="User not found")
        # if not tech_check:
        #     app.logger.info("Technology not found")
        #     return jsonify(status=400, message="Technology not found")
        #
        # title_check = title_validator(title)
        # if not title_check:
        #     app.logger.info("Invalid title")
        #     return jsonify(status=200, message="Invalid title")
        #
        # description_check = description_validator(description)
        # if not description_check:
        #     app.logger.info("Invalid description")
        #     return jsonify(status=200, message="Invalid description")
        #
        # if query_check:
        #     if ((query_check.u_id == user_id) or (user_check.roles != 1)):
        #         query_check.title = title
        #         query_check.description = description
        #         query_check.t_id = tech_check.id
        #         today = datetime.now()
        #         date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        #         query_check.updated_at = date_time_obj
        #         db.session.commit()
        #         response = {"query_id": query_check.id, "title": query_check.title,
        #                     "description": query_check.description, "technology": tech}
        #         app.logger.info("Query changed successfully")
        #         return jsonify(status=200, data=response, message="Query changed successfully")
        #     app.logger.info("User not allowed to edit")
        #     return jsonify(status=404, message="User not allowed to edit")
        # app.logger.info("Query didn't found")
        # return jsonify(status=404, message="Query didn't found")

    @authentication
    def delete(self):
        data = request.get_json() or {}
        query_id = data.get('query_id')
        user_id = get_user_id(self)
        query_check = db.session.query(Queries).filter_by(id=query_id).first()
        user_check = db.session.query(User).filter_by(id=user_id).first()

        if not (query_id and user_id):
            app.logger.info("Query id, user_id required to delete")
            return jsonify(status=404, message="Query id, user_id required to delete")
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=404, message="user not found")
        if query_check:
            if ((query_check.u_id == user_id) or (user_check.roles == 3)):
                delete_comment = db.session.query(Comments).filter_by(q_id=query_id).all()
                if delete_comment:
                    for itr1 in delete_comment:
                        delete_likes_dislikes=Opinion.query.filter_by(c_id=itr1.id).all()
                        for itr2 in delete_likes_dislikes:
                          db.session.delete(itr2)
                          db.session.commit()
                        db.session.delete(itr1)
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

    def get(self):  # send all the comments based on comment_id or u_id or q_id or send all
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        order_by_query_obj = db.session.query(Queries).order_by(Queries.updated_at)
        if not order_by_query_obj:
            app.logger.info("No records found")
            return jsonify(status=404, message="No records found")

        c_list = []
        for itr in order_by_query_obj:
            dt = query_serializer(itr)
            c_list.append(dt)

        app.logger.info("Return queries data")
        return jsonify(status=200, data=get_paginated_list(c_list, '/query', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning queries data")

class UserGetQueryByUserId(Resource):
    def get(self):
        user_id=request.args.get('user_id')
        if not user_id:
            app.logger.info("user_id required")
            return jsonify(status=400,message="user_id required")
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        queries_obj = db.session.query(Queries).filter_by(u_id=user_id).all()
        if not queries_obj:
            app.logger.info("No queries found")
            return jsonify(status=404, message="No queries found")
        queries_list = []
        for itr in queries_obj:
            dt = query_serializer(itr)
            queries_list.append(dt)
        page = f'/user/getqueriesbyuserid?user_id={user_id}'
        app.logger.info("Returning queries data")
        return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=True),
                       message="Returning queries data")


# class UserGetQueryByTitle(Resource):
#     def get(self):
#         title=request.args.get('title')
#         if not title:
#             app.logger.info('title required')
#             return jsonify(status=400,message="title required")
#         queries_obj = db.session.query(Queries).filter_by(title=title).first()
#         if not queries_obj:
#             app.logger.info("No queries found")
#             return jsonify(status=404, message="No queries found")
#         page = f'/user/getquerybytitle?title={title}'
#         app.logger.info("Returning query data")
#         return jsonify(status=200,
#             data=get_paginated_list(query_serializer(queries_obj), page, start=request.args.get('start', 1),
#                                                limit=request.args.get('limit', 3),with_params=True), message="Returning queries data")
#

class UserGetQueryByTitle(Resource):
    def get(self):
        title=request.args.get('title')
        queries_obj = Queries.query.filter(Queries.title.ilike(f'%{title}%')).all()
        # queries_obj = Queries.query.filter_by(title=Queries.title.like(f'{title}%')).all()
        print(queries_obj)
        if not queries_obj:
            app.logger.info("No queries found")
            return jsonify(status=404, message="No queries found")
        queries_list = []
        for itr in queries_obj:
            dt = query_serializer(itr)
            queries_list.append(dt)
        page = f"/user/getquerybytitle?title={title}"
        app.logger.info("Returning query data")
        return jsonify(status=200,
            data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
            limit=request.args.get('limit', 3),with_params=False), message="Returning queries data")



class UserGetQueryByTechnology(Resource):
    def get(self, technology):
        tech_obj = db.session.query(Technologies).filter_by(name=technology).first()
        if not tech_obj:
            app.logger.info("technology not found")
            return jsonify(status=404, message="technology not found")

        queries_obj = db.session.query(Queries).filter_by(t_id=tech_obj.id).all()
        if not queries_obj:
            app.logger.info("No queries found")
            return jsonify(status=404, message="No queries found")
        queries_list = []
        for itr in queries_obj:
            dt = query_serializer(itr)
            queries_list.append(dt)
        page = "user/usergetquerybytechnology"+ technology
        app.logger.info("Returning queries data")
        return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3)),
                       message="Returning queries data")


class SaveQuery(Resource):
    def post(self):
        data = request.get_json() or {}
        query_id = data.get('query_id')
        user_id = data.get('user_id')

        if not (user_id or query_id):
            app.logger.info("query_id, user_id are required fields")
            return jsonify(status=400, message="query_id, user_id are required fields")

        check_user = User.query.filter_by(id=user_id).first()
        check_query = Queries.query.filter_by(id=query_id).first()

        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if not check_query:
            app.logger.info("query not found")
            return jsonify(status=400, message="query not found")

        if not is_active(user_id):
            app.logger.info("User disabled temporarily")
            return jsonify(status=400, message="User disabled temporarily")

        saved_query=SavedQueries.query.filter_by(q_id=query_id).first()
        if saved_query:
            db.session.delete(saved_query)
            db.session.commit()
            app.logger.info("Saved Query removed")
            return jsonify(status=200, message="Saved Query removed")

        today = datetime.now()
        save_query = SavedQueries(user_id,query_id,today,today)

        db.session.add(save_query)
        db.session.commit()
        app.logger.info("Query saved")
        return jsonify(status=200, message="Query saved")

    def get(self):

        data=request.get_json() or {}
        user_id = data.get('user_id')

        check_user = User.query.filter_by(id=user_id).first()
        check_saved_query = SavedQueries.query.filter_by(u_id=user_id).all()
        check_query = Queries.query.filter_by(u_id=user_id).all()

        if not check_user:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")

        if not check_query:
            app.logger.info("no saved_query found")
            return jsonify(status=400, message="no saved_query found")

        if not is_active(user_id):
            app.logger.info("User inactive")
            return jsonify(status=400, message="User inactive")

        saved_query_list=[]
        if check_saved_query:
            for itr in check_query:
                  dt=saved_query_serializer(itr)
                  saved_query_list.append(dt)

        app.logger.info("Returning saved queries")
        return jsonify(status=200,data=get_paginated_list(saved_query_list, '/save', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 2),with_params=False),
                       message="Returning saved queries")


    # def delete(self):
    #     data = request.get_json() or {}
    #     saved_id = data.get('saved_id')
    #     user_id = data.get('user_id')
    #
    #     if not (user_id or saved_id):
    #         app.logger.info("saved_id, user_id are required fields")
    #         return jsonify(status=400, message="saved_id, user_id are required fields")
    #
    #     check_user = User.query.filter_by(id=user_id).first()
    #     check_saved_query = SavedQueries.query.filter_by(id=saved_id).first()
    #
    #     if not check_user:
    #         app.logger.info("user not found")
    #         return jsonify(status=400, message="user not found")
    #
    #     if not check_saved_query:
    #         app.logger.info("no saved_query found")
    #         return jsonify(status=400, message="no saved_query found")
    #
    #     if not is_active(user_id):
    #         app.logger.info("User inactive")
    #         return jsonify(status=400, message="User inactive")
    #
    #     unsave_query = SavedQueries.query.filter_by(id=saved_id).first()
    #     db.session.delete(unsave_query)
    #     db.session.commit()
    #
    #     app.logger.info("Query unsaved")
    #     return jsonify(status=200, message="Query unsaved")