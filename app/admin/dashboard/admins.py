from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments
from app import app, db
from sqlalchemy import or_, and_, desc
import re, ast
from app.authentication import encode_auth_token, authentication,is_active
from app.user.serilalizer.serilalizer import admin_serializer,user_serializer,query_serializer,technology_serializer
from app.user.pagination.pagination import get_paginated_list
from app.authentication import get_user_id,authentication


class getadmins(Resource):
    @authentication
    def get(self):

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        admins_list = []

        admin = User.query.filter(or_(User.roles==2,User.roles==3)).all()

        if not admin:
            app.logger.info("No admin found")
            return jsonify(status=400, message="No admin found")
        for itr in admin:
            dt = admin_serializer(itr)
            admins_list.append(dt)
            print(admins_list)
        return jsonify(status=200,
                       data=get_paginated_list(admins_list, '/getadmins', start=request.args.get('start', 1),
                                               limit=request.args.get('limit', 3),with_params=False),
                       message="Returning all admin's name and ids")

    def put(self): #edit admin users
        user_id=get_user_id(self)
        data=request.get_json() or {}
        change_user_id=data.get('change_user_id')
        new_role=data.get('new_role')
        if not ( change_user_id and new_role):
            app.logger.info("change_user_id and new_role are required")
            return jsonify(status=400,message="change_user_id and new_role are required")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        check_superadmin=User.query.filter_by(id=user_id).first()
        check_admin=User.query.filter_by(id=change_user_id).first()

        if not check_superadmin:
            app.logger.info("superadmin not found")
            return jsonify(status=404, message="user1 not found")
        if not check_admin:
            app.logger.info("admin not found")
            return jsonify(status=404, message="user2 not found")
        if check_superadmin.roles!=3:
            app.logger.info("only superadmin can edit")
            return jsonify(status=404,message="only superadmin can edit")
        if new_role == 3:
            app.logger.info("can't add superadmins")
            return jsonify(status=404, message="can't add superadmins")
        if check_superadmin.roles==3 and check_admin.roles == 2 and check_admin.roles!=3:
            check_admin.roles=new_role
            today = datetime.now()
            check_admin.date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            db.session.commit()
            response = {"name":check_admin.name, "role":check_admin.roles}
            app.logger.info(f'{check_admin.name} Updated successfully')
            return jsonify(status=200, data=response, message="updated Successfully")
        app.logger.info("only admins are editable")
        return jsonify(status=404, message="only admins are editable")

        # admin = User.query.filter(or_(User.roles == 3)).all()

        # if not admin:
        #     app.logger.info("No admin found")
        #     return jsonify(status=400, message="No admin found")
        # for itr in admin:
        #     dt = admin_serializer(itr)
        #     admins_list.append(dt)
        #     print(admins_list)
        # return jsonify(status=200,
        #                data=get_paginated_list(admins_list, '/getadmins', start=request.args.get('start', 1),
        #                                        limit=request.args.get('limit', 3)),
        #                message="Returning all admin's name and ids")

    def delete(self): #delete admin users
        user_id = get_user_id(self)
        data = request.get_json() or {}
        delete_user_id = data.get('delete_user_id')
        if not delete_user_id:
            app.logger.info("delete_user_id required")
            return jsonify(status=400, message="delete_user_id required")

        active = is_active(user_id)
        if not active:
            app.logger.info("admin disabled temporarily")
            return jsonify(status=404, message="admin disabled temporarily")

        check_superadmin= User.query.filter_by(id=user_id).first()
        check_admin = User.query.filter_by(id=delete_user_id).first()

        if not check_superadmin:
            app.logger.info("superadmin not found")
            return jsonify(status=404, message="user1 not found")

        if not check_admin:
            app.logger.info("admin not found")
            return jsonify(status=404, message="user2 not found")

        if check_superadmin.roles!=3:
            app.logger.info("only superadmin can delete")
            return jsonify(status=404,message="only superadmin can edit")

        if check_admin.roles!=2:
            app.logger.info("only admin can be deleted")
            return jsonify(status=404, message="only admin can be deleted")

        if check_superadmin.roles == 3 and (check_admin.roles != 1 or check_admin.roles != 3):
            if check_admin.status:
             check_admin.status = False
            else:
             check_admin.status=True
            today = datetime.now()
            check_admin.date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
            db.session.commit()
            response = {"name": check_admin.name, "status": check_admin.status}
            app.logger.info(f'{check_admin.name} Updated successfully')
            return jsonify(status=200, data=response, message="updated Successfully")

