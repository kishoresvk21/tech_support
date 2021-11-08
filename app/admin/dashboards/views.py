from flask import request,jsonify
from app import app,db
from flask_restplus import Resource
from sqlalchemy import and_, func
from flask_wtf import FlaskForm
from app.models_package.models import User, Queries, Comments, SupportTickets
from app.serializer import user_serializer
from app.pagination import get_paginated_list
from app.utils.update_like_dislike_count import update_like_dislike_count
import re
from datetime import timedelta,datetime
import monthdelta
from dateutil.relativedelta import relativedelta

#
# class FilterRecord(Resource):
#     def get(self):  # from_date,to_date,record_selection
#         from_date = datetime.strptime(request.args.get("from_date"), '%Y-%m-%d')
#         to_date = datetime.strptime(request.args.get("to_date"), '%Y-%m-%d')
#         filter_choice = request.args.get("filter_choice")
#         print(from_date, to_date)
#         next_year = from_date.year
#         while next_year != to_date.year:
#             next_to_date = from_date
#             for itr in range(from_date.month, to_date.month):  # 2021=11-01 to 2022-3-01
#                 next_to_date = next_to_date + monthdelta.monthdelta(months=1)
#                 get_records_from_to = Comments.query.filter(and_(Comments.updated_at >= from_date,
#                                                                  Comments.updated_at <= next_to_date)).count()
#                 print(get_records_from_to)
#                 if itr == 12:
#                     break
#             next_year += 1
#
#         if not (from_date and to_date and filter_choice):
#             app.logger.info("from_date, to_date or filter_choice parameters missing")
#             return jsonify(status=400, message="from_date, to_date or filter_choice parameters missing")
#
#         next_to_date = from_date
#         for itr in range(from_date.month, to_date.month):  # 2021=11-01 to 2022-3-01
#             next_to_date = next_to_date + monthdelta.monthdelta(months=1)
#             get_records_from_to = Comments.query.filter(and_(Comments.updated_at >= from_date,
#                                                              Comments.updated_at <= next_to_date)).count()
#             print(get_records_from_to)
#
#         return
#         # to_date = (from_date+monthdelta.monthdelta(months=1))-timedelta(days=1)
#         # print(from_date,to_date)
#         # get_records_from_to = Comments.query.filter(and_(Comments.updated_at >= from_date,
#         #                                                  Comments.updated_at <= to_date)).count()
#         # print(get_records_from_to)
#         # return
#
#         if filter_choice not in ("users", "queries", "comments"):
#             app.logger.info("incorrect filter_choice")
#             return jsonify(status=400, message="incorrect filter_choice")
#
#         for month_itr in range(from_month, to_month):
#
#             if filter_choice == "users":
#                 get_records_from_to = User.query.filter(and_(User.updated_at >= itr_from_date,
#                                                              User.updated_at < itr_to_date)).count()
#             elif filter_choice == "queries":
#                 get_records_from_to = Queries.query.filter(and_(Queries.updated_at >= itr_from_date,
#                                                                 Queries.updated_at < itr_to_date)).count()
#             elif filter_choice == "comments":
#                 get_records_from_to = Comments.query.filter(and_(Comments.updated_at >= itr_from_date,
#                                                                  Comments.updated_at < itr_to_date)).count()
#             else:
#                 app.logger.info("record selection should be users, queries, comments")
#                 return jsonify(status=400, message="record selection should be users, queries, comments")
#
#             dt = dict(from_date=itr_from_date, to_date=itr_to_date, count=get_records_from_to)
#             month_wise_count.append(dt)
#         app.logger.info(f"month wise count from {from_date} to {to_date}")
#         page = '/admin/datefilter?from_date=' + f'{from_date}' + \
#                "&to_date=" + f'{to_date}' + "&filter_choice=" + f'{filter_choice}'
#         return jsonify(status=200, data=get_paginated_list(month_wise_count, page, start=request.args.get('start', 1),
#                                                            limit=request.args.get('limit', 3), with_params=False),
#                        message=f"month wise count from {from_date} to {to_date}")
#


class FilterRecord(Resource):
    def get(self):  # from_date,to_date,record_selection
        year = request.args.get("year")
        if not (year):
            app.logger.info("year is required")
            return jsonify(status=400, message="year is required")
        from_date= datetime.strptime(f'{year}-01-01','%Y-%m-%d')
        # to_date = datetime.strptime(f'{str(int(year)+1)}-01-01','%Y-%m-%d')
        # from_date = datetime.strptime(request.args.get("from_date"), '%Y-%m-%d')
        # to_date = datetime.strptime(request.args.get("to_date"), '%Y-%m-%d')
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
            tickets_count = SupportTickets.query.filter(and_(SupportTickets.updated_at >= itr_from_date,
                                                                 SupportTickets.updated_at < itr_to_date)).count()
            resolved_tickets_count = SupportTickets.query.filter(and_(SupportTickets.status == 0,
                                                                SupportTickets.updated_at >= itr_from_date,
                                                                 SupportTickets.updated_at < itr_to_date)).count()

            dt = dict(user_count=user_count,
                      queries_count=queries_count,
                      comments_count=comments_count,
                      tickets_count=tickets_count,
                      resolved_tickets_count=resolved_tickets_count,
                      month=month_itr)

            itr_from_date=itr_to_date
            month_wise_count.append(dt)
        # return jsonify(month_wise_count)
        app.logger.info(f"month wise count for year {year}")
        return jsonify(status=200, data=month_wise_count, message=f"month wise count for year {year}")


class TopUsersList(Resource):
    def get(self):  # send all the comments based on user_id
        update_like_dislike_count(self)
        users_limit=request.args.get('users_limit')
        top_users_list = []
        count = 0
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


