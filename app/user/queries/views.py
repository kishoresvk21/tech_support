from flask_restplus import Resource
from app.authentication import authentication
from flask import request, jsonify
from app import app, db
from sqlalchemy import or_, and_
from app.models_package.models import User, Technologies, Queries, Comments, SavedQueries, LikesDislikes
from datetime import datetime
from app.pagination import get_paginated_list
from app.serializer import query_serializer
from app.authentication import is_active, get_user_id
from app.utils.form_validation import title_validator, description_validator
from app.utils.file_upload import upload_file


class QueriesClass(Resource):
    @authentication
    def post(self):
        file = request.files.get('file')
        try:
            title = request.form['title']
            user_id = request.form['user_id']
            print(type(user_id))
            description = request.form['description']
            tech = request.form['technology']
        except:
            app.logger.info("title, description, user_id and technology are required")
            return jsonify(status=400, message="title, description, user_id and technology are required")
        if not is_active(user_id):
            app.logger.info("User is temporarily disabled")
            return jsonify(status=404, message="User is temporarily disabled")
        if not title_validator(title):
            app.logger.info("Invalid title length")
            return jsonify(status=400, message="Invalid title length")
        if not description_validator(description):
            app.logger.info("Invalid description length")
            return jsonify(status=400, message="Invalid description length")
        user_check = User.query.filter_by(id=user_id).first()
        print(type(user_check.id))
        tech_check = Technologies.query.filter_by(name=tech).first()
        if not tech_check:
            app.logger.info("technology not found")
            return jsonify(status=400, message="technology not found")
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        query_insertion = Queries.query.filter(or_(Queries.title == title,
                                                   Queries.description == description)).all()

        if query_insertion:
            for itr in query_insertion:
                if itr.title == title:
                    app.logger.info("Data already exist")
                    return jsonify(status=400, message="Data already exist")

        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        try:
            if file:
                file_path = upload_file(self, file)
            else:
                file_path = None
            question = Queries(user_id, title, description, tech_check.id, date_time_obj, date_time_obj, file_path)
            db.session.add(question)
            db.session.commit()
        except:
            app.logger.info("DB Error")
            return jsonify(status=400, message="DB Error")
        app.logger.info("Query inserted successfully")
        response = query_serializer(question)
        return jsonify(status=200, data=response, message="Query inserted successfully")

    @authentication
    def put(self):
        new_file = request.files.get('file')
        try:
            title = request.form['title']
            user_id = request.form['user_id']
            query_id = request.form['query_id']
            description = request.form['description']
            tech = request.form['technology']
        except:
            app.logger.info("title, description, user_id, query_id and technology are required")
            return jsonify(status=400, message="title, description, user_id, query_id and technology are required")

        if not (query_id and user_id and tech and title and description):
            app.logger.info("query_id, user_id, technology, title and description are required fields")
            return jsonify(status=400, message="query_id, user_id, technology, title and description are required fields")

        if not title_validator(title):
            app.logger.info("Invalid title length")
            return jsonify(status=400, message="Invalid title length")

        if not description_validator(description):
            app.logger.info("Invalid description length")
            return jsonify(status=400, message="Invalid description length")

        user_check = User.query.filter_by(id=user_id).first()
        tech_check = Technologies.query.filter_by(name=tech).first()
        query_check = Queries.query.filter_by(id=query_id).first()

        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        if not tech_check:
            app.logger.info("technology not found")
            return jsonify(status=400, message="technology not found")
        if not query_check:
            app.logger.info("query not found")
            return jsonify(status=400, message="query not found")
        if query_check:
            if query_check.u_id == int(user_id):
                query_insertion_title = Queries.query.filter_by(title=title).all()
                if query_insertion_title:
                    for itr in query_insertion_title:
                        if itr.title == title:
                            app.logger.info("Data already exist")
                            return jsonify(status=400, message="Data already exist")

                query_check.title = title
                query_check.description = description
                query_check.t_id = tech_check.id
                today = datetime.now()
                query_check.updated_at = today
                if new_file:
                    file_data = upload_file(self, new_file)
                    new_file_name = file_data
                    # new_file_path = file_data[1]
                    query_check.file_path = new_file_name
                else:
                    new_file_name = None
                    # new_file_path = None

                # edit_comment_by_id.filepath = new_file_path
                db.session.commit()
                response = {"query_id": query_check.id, "title": query_check.title,
                            "description": query_check.description, "technology": tech}
                app.logger.info("Query changed successfully")
                return jsonify(status=200, data=response, message="Query changed successfully")
            app.logger.info("User not allowed to edit")
            return jsonify(status=404, message="User not allowed to edit")
        app.logger.info("Query didn't found")
        return jsonify(status=404, message="Query didn't found")

    # def put(self):
    #     data = request.get_json() or {}
    #     if not data:
    #         app.logger.info("No input(s)")
    #         return jsonify(status=400, message="No input(s)")
    #     query_id = data.get('query_id')
    #     user_id = data.get('user_id')
    #     tech = data.get('technology')
    #     title = data.get('title')
    #     description = data.get('description')
    #
    #     if not (query_id and user_id and tech and title and description):
    #         app.logger.info("query_id, user_id, technology, title and description are required fields")
    #         return jsonify(status=400, message="query_id, user_id, technology, title and description are required fields")
    #
    #     if not title_validator(title):
    #         app.logger.info("Invalid title length")
    #         return jsonify(status=400, message="Invalid title length")
    #
    #     if not description_validator(description):
    #         app.logger.info("Invalid description length")
    #         return jsonify(status=400, message="Invalid description length")
    #
    #     user_check = User.query.filter_by(id=user_id).first()
    #     tech_check = Technologies.query.filter_by(name=tech).first()
    #     query_check = Queries.query.filter_by(id=query_id).first()
    #     if not user_check:
    #         app.logger.info("User not found")
    #         return jsonify(status=400, message="User not found")
    #     if not tech_check:
    #         app.logger.info("technology not found")
    #         return jsonify(status=400, message="technology not found")
    #     if not query_check:
    #         app.logger.info("query not found")
    #         return jsonify(status=400, message="query not found")
    #     if query_check:
    #         if query_check.u_id == user_id:
    #             query_check.title = title
    #             query_check.description = description
    #             query_check.t_id = tech_check.id
    #             today = datetime.now()
    #             query_check.updated_at = today
    #             db.session.commit()
    #             response = {"query_id": query_check.id, "title": query_check.title,
    #                         "description": query_check.description, "technology": tech}
    #             app.logger.info("Query changed successfully")
    #             return jsonify(status=200, data=response, message="Query changed successfully")
    #         app.logger.info("User not allowed to edit")
    #         return jsonify(status=404, message="User not allowed to edit")
    #     app.logger.info("Query didn't found")
    #     return jsonify(status=404, message="Query didn't found")

    # @authentication
    def delete(self):
        data = request.get_json() or {}
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        try:
            query_id = data.get('query_id')
            user_id = data.get('user_id')
            query_check = Queries.query.filter_by(id=query_id).first()
            user_check = User.query.filter_by(id=user_id).first()
        except:
            app.logger.info("user_id/query_id not found")
            return jsonify(status=400, message="user_id/query_id not found")

        if not (query_id and user_id):
            app.logger.info("Query id, user_id required to delete")
            return jsonify(status=404, message="Query id, user_id required to delete")

        if query_check:
            if ((query_check.u_id == user_id) or (user_check.roles == 2) or (user_check.roles == 3)):
                delete_comment = Comments.query.filter_by(q_id=query_id).all()
                if delete_comment:
                    for itr in delete_comment:
                        delete_likes_dislikes_comment = LikesDislikes.query.filter_by(c_id=itr.id).all()
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

    @authentication
    def get(self):
        logged_in_user_id = get_user_id(self)
        active = is_active(logged_in_user_id)
        if not active:
            app.logger.info("User disabled temporarily")
            return jsonify(status=404, message="User disabled temporarily")

        page = request.args.get('page', 1, type=int)
        order_by_query_obj = db.session.query(Queries).order_by(Queries.updated_at).paginate(per_page=5, page=page)

        if not order_by_query_obj:
            app.logger.info("No Queries in DB")
            return jsonify(status=404, message="No Queries in DB")

        c_list = []

        for itr in order_by_query_obj.items:
            dt = query_serializer(itr, logged_in_user_id)
            c_list.append(dt)
        return jsonify(status=200, data=c_list)

        # for itr in order_by_query_obj:
        #     dt = query_serializer(itr)
        #     c_list.append(dt)
        #
        # app.logger.info("Return queries data")
        # return jsonify(status=200, data=get_paginated_list(c_list, '/query', start=request.args.get('start', 1),
        #                                                    limit=request.args.get('limit', 3),with_params=False),
        #                message="Returning queries data")


class GetQueryByUserId(Resource):
    def get(self, user_id):
        queries_obj = db.session.query(Queries).filter_by(u_id=user_id).all()
        if not queries_obj:
            app.logger.info("No queries found")
            return jsonify(status=404, message="No queries found")
        queries_list = []
        for itr in queries_obj:
            dt = query_serializer(itr)
            queries_list.append(dt)
        user_id_str = str(user_id)
        page = '/getqueries/user/' + user_id_str
        app.logger.info("Returning queries data")
        return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning queries data")


class GetQueryByTitle(Resource):
    def get(self, title):
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
        page = '/getqueries/title/' + title
        app.logger.info("Returning query data")
        return jsonify(status=200,
            data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
            limit=request.args.get('limit', 3),with_params=False), message="Returning queries data")


class GetQueryByTechnology(Resource):
    def get(self, tech_id):
        tech_obj = Technologies.query.filter_by(id=tech_id).first()
        if not tech_obj:
            app.logger.info("technology not found")
            return jsonify(status=404, message="technology not found")
        queries_obj = Queries.query.filter_by(t_id=tech_obj.id).all()
        if not queries_obj:
            app.logger.info("No queries found")
            return jsonify(status=404, message="No queries found")
        queries_list = []
        for itr in queries_obj:
            dt = query_serializer(itr)
            queries_list.append(dt)
        page = '/getqueries/technology/' + str(tech_id)
        app.logger.info("Returning queries data")
        return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning queries data")


class SaveQuery(Resource):
    def post(self):
        data = request.get_json() or {}
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        query_id = data.get('query_id')
        user_id = data.get('user_id')

        if not (user_id or query_id):
            app.logger.info("query_id, user_id are required fields")
            return jsonify(status=400, message="query_id, user_id are required fields")

        check_user = User.query.filter_by(id=user_id).first()
        check_query = Queries.query.filter_by(id=query_id).first()

        if not (check_user and check_query):
            app.logger.info("Data not found")
            return jsonify(status=400, message="Data not found")

        if not is_active(user_id):
            app.logger.info("User inactive")
            return jsonify(status=400, message="User inactive")

        saved = SavedQueries.query.filter(and_(SavedQueries.u_id == user_id,
                                                      SavedQueries.q_id == query_id)).first()
        if saved:
            db.session.delete(saved)
            db.session.commit()
            app.logger.info("Query unsaved")
            return jsonify(status=200, message="Query sunaved")
        else:
            today = datetime.now()
            save_query = SavedQueries(user_id, query_id, today, today)
            db.session.add(save_query)
            db.session.commit()
            app.logger.info("Query saved")
            return jsonify(status=200, message="Query saved")


    # def delete(self):
    #     data = request.get_json() or {}
    #     if not data:
    #         app.logger.info("No input(s)")
    #         return jsonify(status=400, message="No input(s)")
    #
    #     saved_query_id = data.get('saved_query_id')
    #     user_id = data.get('user_id')
    #
    #     if not (user_id or saved_query_id):
    #         app.logger.info("query_id, user_id are required fields")
    #         return jsonify(status=400, message="query_id, user_id are required fields")
    #
    #
    #     check_user = User.query.filter_by(id=user_id).first()
    #     check_saved_query = SavedQueries.query.filter_by(id=saved_query_id).first()
    #
    #     if not (check_user and check_saved_query):
    #         app.logger.info("Data not found")
    #         return jsonify(status=400, message="Data not found")
    #
    #     if not is_active(user_id):
    #         app.logger.info("User inactive")
    #         return jsonify(status=400, message="User inactive")
    #
    #
    #     db.session.commit()
    #
    #     app.logger.info("Query unsaved")
    #     return jsonify(status=200, message="Query unsaved")











