from flask_restplus import Resource
from app.authentication import authentication
from flask import request, jsonify
from app import app, db
from app.models_package.models import User, SupportTickets
from datetime import datetime
from app.pagination import get_paginated_list
from app.serializer import support_ticket_serializer
from app.authentication import is_active
from app.utils.form_validation import title_validator, description_validator
from app.utils.file_upload import upload_file
from app.utils.smtp_mail import mail_for_support_ticket


class Support(Resource):
    @authentication
    def post(self):
        file = request.files.get('file')
        try:
            title = request.form['title']
            user_id = request.form['user_id']
            print(type(user_id))
            description = request.form['description']
        except:
            app.logger.info("title, description and user_id are required")
            return jsonify(status=400, message="title, description and user_id are required")
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
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")

        today = datetime.now()
        # date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        try:
            if file:
                file_path = upload_file(self, file)
            else:
                file_path = None
            ticket = SupportTickets(user_id, title, description, file_path, today, today)
            db.session.add(ticket)
            db.session.commit()
            print(ticket)
            mail_for_support_ticket(ticket)
        except:
            app.logger.info("DB Error")
            return jsonify(status=400, message="DB Error")
        app.logger.info("Query inserted successfully")
        response = support_ticket_serializer(ticket)
        return jsonify(status=200, data=response, message="Support ticket inserted successfully")

    @authentication
    def put(self):
        new_file = request.files.get('file')
        try:
            title = request.form['title']
            user_id = request.form['user_id']
            support_ticket_id = request.form['support_ticket_id']
            description = request.form['description']
        except:
            app.logger.info("title, description, user_id and support_ticket_id are required")
            return jsonify(status=400, message="title, description, user_id and support_ticket_id are required")

        if not (support_ticket_id and user_id and title and description):
            app.logger.info("support_ticket_id, user_id, title and description are required fields")
            return jsonify(status=400, message="support_ticket_id, user_id, title and description are required fields")

        if not title_validator(title):
            app.logger.info("Invalid title length")
            return jsonify(status=400, message="Invalid title length")

        if not description_validator(description):
            app.logger.info("Invalid description length")
            return jsonify(status=400, message="Invalid description length")

        user_check = User.query.filter_by(id=user_id).first()
        support_ticket_check = SupportTickets.query.filter_by(id=support_ticket_id).first()

        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        if not support_ticket_check:
            app.logger.info("Ticket not found")
            return jsonify(status=400, message="Ticket not found")
        if support_ticket_check:
            if support_ticket_check.u_id == int(user_id):
                support_ticket_check.title = title
                support_ticket_check.description = description
                support_ticket_check.updated_at = datetime.now()
                if new_file:
                    file_data = upload_file(self, new_file)
                    new_file_name = file_data
                    # new_file_path = file_data[1]
                    support_ticket_check.name = new_file_name
                else:
                    support_ticket_check.name = None
                    # new_file_path = None

                # edit_comment_by_id.filepath = new_file_path
                db.session.commit()
                response = support_ticket_serializer(support_ticket_check)
                app.logger.info("Ticket changed successfully")
                return jsonify(status=200, data=response, message="Ticket changed successfully")
            app.logger.info("User not allowed to edit")
            return jsonify(status=404, message="User not allowed to edit")
        app.logger.info("Ticket not found")
        return jsonify(status=404, message="Ticket not found")

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

'''''
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

    def get(self):
        page = request.args.get('page', 1, type=int)
        order_by_query_obj = db.session.query(Queries).order_by(Queries.updated_at).paginate(per_page=5, page=page)
        print(order_by_query_obj)
        print(dir(order_by_query_obj))
        if not order_by_query_obj:
            app.logger.info("No Queries in DB")
            return jsonify(status=404, message="No Queries in DB")

        c_list = []

        for itr in order_by_query_obj.items:
            dt = query_serializer(itr)
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
'''''
