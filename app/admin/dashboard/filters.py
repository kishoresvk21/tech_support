from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments
from app import app, db
from sqlalchemy import or_, and_, desc
import re, ast
from app.authentication import encode_auth_token, authentication
from app.user.serilalizer.serilalizer import admin_serializer,user_serializer,query_serializer,technology_serializer
from app.user.pagination.pagination import get_paginated_list
from app.utils.date_validation import validate
import monthdelta
#
# class FilterRecord(Resource):
#     def get(self):
#         from_date = datetime.strptime(request.args.get("from_date"), '%Y-%m-%d')
#         to_date = datetime.strptime(request.args.get("to_date"), '%Y-%m-%d')
#         if not (from_date and to_date):
#             app.logger.info("from_date, to_date are required fields")
#             return jsonify(status=400, message="from_date, to_date or filter_choice parameters missing")
#         month_wise_count=[]
#         for month_itr in range(from_date.month, int(to_date.month)+1):
#             itr_to_date = from_date + monthdelta.monthdelta(months=1)
#             user_count = User.query.filter(and_(User.updated_at >=from_date,
#                                                              User.updated_at < itr_to_date)).count()
#             queries_count = Queries.query.filter(and_(Queries.updated_at >= from_date,
#                                                                 Queries.updated_at < itr_to_date)).count()
#             comments_count = Comments.query.filter(and_(Comments.updated_at >= from_date,
#                                                                  Comments.updated_at < itr_to_date)).count()
#             dt = dict(user_count=user_count,queries_count=queries_count,comments_count=comments_count,month=month_itr)
#             from_date=itr_to_date
#             month_wise_count.append(dt)
#
#         app.logger.info(f"month wise count from {from_date} to {to_date}")
#         return jsonify(status=200, data=month_wise_count,
#                        message=f"month wise count from {from_date} to {to_date}")

class FilterRecord(Resource):
    def get(self):  # from_date,to_date,record_selection
        year=request.args.get("year")
        if not (year):
            app.logger.info("year is required")
            return jsonify(status=400, message="year is required")
        try:
         from_date= datetime.strptime(f'{year}-01-01','%Y-%m-%d')
        except ValueError as e:
            app.logger.info(e)
            return jsonify(status=400,message="Invalid format")
        month_wise_count=[]
        itr_from_date = from_date
        for month_itr in range(1, 13):
            itr_to_date = itr_from_date + monthdelta.monthdelta(months=1)
            user_count = User.query.filter(and_(User.updated_at >=itr_from_date,
                                                             User.updated_at < itr_to_date)).count()
            queries_count = Queries.query.filter(and_(Queries.updated_at >= itr_from_date,
                                                                Queries.updated_at < itr_to_date)).count()
            comments_count = Comments.query.filter(and_(Comments.updated_at >= itr_from_date,
                                                                 Comments.updated_at < itr_to_date)).count()
            dt = dict(user_count=user_count,queries_count=queries_count,comments_count=comments_count,month=month_itr)
            itr_from_date=itr_to_date
            month_wise_count.append(dt)
        app.logger.info(f"month wise count for year {year}")
        return jsonify(status=200, data=month_wise_count,
                       message=f"month wise count for year {year}")

