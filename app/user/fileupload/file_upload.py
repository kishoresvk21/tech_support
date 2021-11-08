from flask import Flask, flash, request, redirect, url_for,jsonify
from werkzeug.utils import secure_filename
from app import app
from flask_restplus import Resource
from app.user.models.models import Files,db
from flask_sqlalchemy import SQLAlchemy
import os
from flask import send_from_directory
from datetime import datetime
import os
from app.user.models.models import User,Comments,Queries
from sqlalchemy import and_

class download(Resource):
  def get(self):
      cwd = os.getcwd()
      folder = "UPLOAD"
      path = os.path.join(cwd, folder)
      data=request.get_json() or {}
      user_id=data.get('user_id')
      comment_id=data.get('comment_id')
      query_id=data.get('query_id')
      if not (user_id and (comment_id or query_id)):
          app.logger.info('user_id and comment_id or query_id are required')
          return jsonify(status=400, message='user_id and comment_id or query_id are required')
      user_check = User.query.filter_by(id=user_id).first()
      if not user_check:
          app.logger.info('user not found')
          return jsonify(status=400, message="user not found")
      if comment_id:
         comment_check = Comments.query.filter_by(id=comment_id).first()
         if not comment_check:
            app.logger.info('comment not found')
            return jsonify(status=400, message="comment not found")
         try:
           file=Comments.query.filter(Comments.id==comment_id).first()
           print(file)
           filename=file.filename
           return send_from_directory(path,filename)
         except:
           app.logger.info("No records found")
           return jsonify(status=200,message="No records found")
      elif query_id:
          query_check = Queries.query.filter_by(id=query_id).first()
          if not query_check:
              app.logger.info('query not found')
              return jsonify(status=400, message="query not found")
          try:
              file = Queries.query.filter(Queries.id == query_id).first()
              filename = file.filename
              return send_from_directory(path, filename)
          except:
              app.logger.info("No records found")
              return jsonify(status=200, message="No records found")


def upload_file(self,file):
    cwd = os.getcwd()
    folder = "UPLOAD"
    path = os.path.join(cwd, folder)
    if not os.path.exists(path):
       os.mkdir(path)
    if not file:
        app.logger.info('file required')
        return jsonify(status=400, message="file required")
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(path, filename))
        path = f'{path}/{filename}'
        return filename,path
    return


# class upload(Resource):
#   def post(self):
#    UPLOAD_FOLDER = '/home/ureyanarasimha/UPLOAD'
#    # ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
#    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#    user_id=request.form['u_id']
#    comment_id=request.form['c_id']
#    if not (user_id and comment_id):
#        app.logger.info('user_id and comment_id are required')
#        return jsonify(status=400, message="user_id and comment_id are required")
#    file = request.files.getlist('file[]')
#    # file = request.files.get('file')
#    if not file:
#         app.logger.info('file is required')
#         return jsonify(status=400,message="file is required")
#    for itr in file:
#     if itr:
#         filename = secure_filename(itr.filename)
#         itr.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         path=f'{UPLOAD_FOLDER}/{filename}'
#         print(path)
#         today = datetime.now()
#         date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#         newfile = Files(filename,path,user_id,comment_id,date_time_obj,date_time_obj)
#         db.session.add(newfile)
#         db.session.commit()
#    app.logger.info('file uploded succesfully')
#    return jsonify(status=200, message="file uploded succesfully")
#
#   def get(self):
#       UPLOAD_FOLDER = '/home/ureyanarasimha/UPLOAD'
#       app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#       # file = request.files['file']
#       file = request.files.getlist('file[]')
#       if not file:
#           app.logger.info('file required')
#           return jsonify(status=400, message="file required")
#       while(1):
#        for itr in file:
#           if itr:
#              filename = secure_filename(itr.filename)
#              print(filename)
#              return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
#              # x=send_from_directory(app.config["UPLOAD_FOLDER"], filename)
#              # return x

# class upload(Resource):
#   def post(self):
#    UPLOAD_FOLDER = '/home/ureyanarasimha/UPLOAD'
#    # ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
#    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#    user_id=request.form['u_id']
#    comment_id=request.form['c_id']
#    if not (user_id and comment_id):
#        app.logger.info('user_id and comment_id are required')
#        return jsonify(status=400, message="user_id and comment_id are required")
#    # file = request.files.getlist('file[]')
#    file = request.files.get('file')
#    if not file:
#         app.logger.info('file is required')
#         return jsonify(status=400,message="file is required")
#    if file:
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         path=f'{UPLOAD_FOLDER}/{filename}'
#         print(path)
#         today = datetime.now()
#         date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#         newfile = Files(filename,path,user_id,comment_id,date_time_obj,date_time_obj)
#         db.session.add(newfile)
#         db.session.commit()
#    app.logger.info('file uploded succesfully')
#    return jsonify(status=200, message="file uploded succesfully")
#
#   def get(self):
#       UPLOAD_FOLDER = '/home/ureyanarasimha/UPLOAD'
#       app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#       file = request.files.get('file')
#       # file = request.files.getlist('file[]')
#       if not file:
#           app.logger.info('file required')
#           return jsonify(status=400, message="file required")
#       if itr:
#          filename = secure_filename(itr.filename)
#          print(filename)
#          return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
#              # x=send_from_directory(app.config["UPLOAD_FOLDER"], filename)
#              # return x

# class upload(Resource):
#   def post(self):
#       cwd = os.getcwd()
#       folder="UPLOAD"
#       path = os.path.join(cwd,folder)
#       if not os.path.exists(path):
#           os.mkdir(path)
#       try:
#        user_id = request.form['user_id']
#        comment_id = request.form['comment_id']
#       except:
#         app.logger.info('user_id and comment_id are required')
#         return jsonify(status=400, message="user_id and comment_id are required")
#       # file = request.files.getlist('file[]')
#       file = request.files.get('file')
#       if not file:
#           app.logger.info('file is required')
#           return jsonify(status=400, message="file is required")
#
#       user_check=User.query.filter_by(id=user_id).first()
#       if not user_check:
#           app.logger.info('user not found')
#           return jsonify(status=400, message="user not found")
#
#       comment_check=Comments.query.filter_by(id=comment_id).first()
#       if not comment_check:
#           app.logger.info('comment not found')
#           return jsonify(status=400, message="comment not found")
#
#       if file:
#           filename = secure_filename(file.filename)
#           file.save(os.path.join(path,filename))
#           path = f'{path}/{filename}'
#           print(path)
#           today = datetime.now()
#           date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#           newfile = Files(filename, path, user_id, comment_id, date_time_obj, date_time_obj)
#           db.session.add(newfile)
#           db.session.commit()
#       app.logger.info('file uploded succesfully')
#       return jsonify(status=200, message="file uploded succesfully")
#   def get(self):
#       # UPLOAD_FOLDER = '/home/ureyanarasimha/UPLOAD'
#       # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#       # file = request.files.get('file')
#       # file = request.files.getlist('file[]')
#       cwd = os.getcwd()
#       folder = "UPLOAD"
#       path = os.path.join(cwd, folder)
#       print(path)
#       data=request.get_json() or {}
#       user_id=data.get('user_id')
#       comment_id=data.get('comment_id')
#       if not user_id and comment_id:
#           app.logger.info('user_id and comment_id are required')
#           return jsonify(status=400, message='user_id and comment_id are required')
#       user_check = User.query.filter_by(id=user_id).first()
#       if not user_check:
#           app.logger.info('user not found')
#           return jsonify(status=400, message="user not found")
#
#       comment_check = Comments.query.filter_by(id=comment_id).first()
#       if not comment_check:
#         app.logger.info('comment not found')
#         return jsonify(status=400, message="comment not found")
#
      # try:
      #      file=Comments.query.filter(and_(Comments.u_id==user_id,Comments.c_id==comment_id)).first()
      #      filename=file.name
      #      return send_from_directory(path,filename)
      # except:
      #         app.logger.info("No records found")
      #         return jsonify(status=200,message="No records found")
