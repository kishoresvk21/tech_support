from flask_restplus import Resource
from flask import request
from app.user.models.models import Comments
from flask import jsonify
from app import app,db
from app.user.models.models import User,Opinion
from datetime import datetime
from sqlalchemy import and_
from app.utils.count import update_like_dislike_count
from app.authentication import get_user_id,authentication
from app.user.serilalizer.serilalizer import opinion_serializer

class Like(Resource):
    @authentication
    def post(self):
        user_id=get_user_id(self)
        data=request.get_json() or {}
        comment_id=data.get('comment_id')
        if not (comment_id):
             app.logger.info("comment_id required")
             return jsonify(status=400,message="comment_id required")
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        user_obj=User.query.filter_by(id=user_id).first()
        comment_obj=Comments.query.filter_by(id=comment_id).first()
        if not user_obj:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if not comment_obj:
            app.logger.info("comment not found")
            return jsonify(status=400, message="comment not found")
        opinion_obj=Opinion.query.filter(and_(Opinion.u_id==user_id,
                                                           Opinion.c_id==comment_id)).first()
        if opinion_obj:
            if opinion_obj.dislike:
                opinion_obj.like= True
                opinion_obj.dislike = False
                db.session.commit()
                update_like_dislike_count(self)
                app.logger.info("liked")
                return jsonify(status=200,data=opinion_serializer(opinion_obj),message="liked")
            else:
                db.session.delete(opinion_obj)
                db.session.commit()
                update_like_dislike_count(self)
                app.logger.info("like removed")
                return jsonify(status=200,data=opinion_serializer(opinion_obj),message="like removed")

        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        like = True
        dislike = False
        like_dislike_record = Opinion(user_id, comment_id, like, dislike, date_time_obj, date_time_obj)
        db.session.add(like_dislike_record)
        db.session.commit()
        update_like_dislike_count(self)
        app.logger.info("Liked")
        return jsonify(status=200,data=opinion_serializer(like_dislike_record),message="Liked")

class DisLike(Resource):
    def post(self):
        data=request.get_json() or {}
        user_id=data.get('user_id')
        comment_id=data.get('comment_id')
        if not (user_id and comment_id):
             app.logger.info("user_id and comment_id are required")
             return jsonify(status=400,message="user_id and comment_id are required")
        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=400, message="user disabled temporarily")
        user_obj=User.query.filter_by(id=user_id).first()
        comment_obj=Comments.query.filter_by(id=comment_id).first()
        if not user_obj:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if not comment_obj:
            app.logger.info("comment not found")
            return jsonify(status=400, message="comment not found")
        opinion_obj = Opinion.query.filter(and_(Opinion.u_id == user_id,
                                                             Opinion.c_id == comment_id)).first()
        if  opinion_obj:
            if opinion_obj.like:
                opinion_obj.like = False
                opinion_obj.dislike = True
                db.session.commit()
                update_like_dislike_count(self)
                app.logger.info("disliked")
                return jsonify(status=200,data=opinion_serializer(opinion_obj),message="disliked")
            else:
                db.session.delete(opinion_obj)
                db.session.commit()
                update_like_dislike_count(self)
                app.logger.info("like or dislike removed")
                return jsonify(status=200,data=opinion_serializer(opinion_obj),message="like or dislike removed")

        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        like = False
        dislike = True
        like_dislike_record = Opinion(user_id, comment_id, like, dislike, date_time_obj, date_time_obj)
        db.session.add(like_dislike_record)
        db.session.commit(self)
        update_like_dislike_count()
        app.logger.info("DisLiked")
        return jsonify(status=200,data=opinion_serializer(like_dislike_record),message="DisLiked")