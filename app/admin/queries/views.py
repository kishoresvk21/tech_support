from flask_restplus import Resource
from app.authentication import authentication
from flask import request,jsonify
from app import app,db
from sqlalchemy import or_, and_
from app.models_package.models import User,Technologies,Queries,Comments,LikesDislikes
from datetime import datetime
from app.pagination import get_paginated_list
from app.serializer import query_serializer

class QueriesClass(Resource):
    @authentication
    def delete(self):
        data = request.get_json() or {}
        query_id = data.get('query_id')
        user_id = data.get('user_id')
        if not (query_id and user_id):
            app.logger.info("Query id, user_id required to delete")
            return jsonify(status=404, message="Query id, user_id required to delete")

        query_check = db.session.query(Queries).filter_by(id=query_id).first()
        user_check = db.session.query(User).filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if not query_check:
            app.logger.info("query not found")
            return jsonify(status=400, message="query not found")
        if query_check:
            if user_check.roles == 2 or user_check.roles==3:  # admin or super admin can delete
                delete_comment = db.session.query(Comments).filter_by(q_id=query_id).all()
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

    def get(self):  # send all the queries
        order_by_query_obj = db.session.query(Queries).order_by(Queries.updated_at)
        if not order_by_query_obj:
            app.logger.info("No Queries in DB")
            return jsonify(status=404, message="No Queries in DB")
        c_list = []
        for itr in order_by_query_obj:
            dt = query_serializer(itr)
            c_list.append(dt)
        app.logger.info("Return queries data")
        return jsonify(status=200, data=get_paginated_list(c_list, '/admin/query', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning queries data")


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
        page = '/admin/getqueries/user/' + user_id_str
        app.logger.info("Returning queries data")
        return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning queries data")


class GetQueryByTitle(Resource):
    def get(self, title):
        queries_obj = Queries.query.filter_by(title=title).all()
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
            limit=request.args.get('limit', 3)), message="Returning queries data")


class GetQueryByTechnology(Resource):
    def get(self, technology):
        tech_obj = Technologies.query.filter_by(name=technology).first()
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
        page = '/getqueries/technology/' + technology
        app.logger.info("Returning queries data")
        return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3)),
                       message="Returning queries data")

class Unanswered(Resource):
    def get(self):
        unanswered_queries_obj_list = []
        unanswered_queries_list = []

        r = db.session.query(Queries, Comments).outerjoin(Comments, Queries.id == Comments.q_id).all()
        if not r:
            app.logger.info("no records found")
            return jsonify(status=404, message="no records found")

        for result in r:
            print(result)
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
        return jsonify(status=200,data=get_paginated_list(unanswered_queries_list, '/admin/query/unanswered', start=request.args.get('start', 1),
                                          limit=request.args.get('limit', 3),with_params=False),message="Returning unanswered queries data")