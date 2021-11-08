from flask import request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from app import app
from flask_restplus import Resource
from app.models_package.models import Files
from app import db
import os
from datetime import datetime
# from app.utils.convert_file import file_print
from app.models_package.models import User, Comments, Queries


def upload_file(self, file):
    cwd = os.getcwd()
    folder = "UPLOAD"
    path = os.path.join(cwd, folder)
    if not os.path.exists(path):
       os.mkdir(path)
    print(file)
    if not file:
        app.logger.info('file required')
        return jsonify(status=400, message="file required")
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(path, filename))
        # path = f'{path}/{filename}'
        # print(path)
        return filename
    return


class Download(Resource):
    # @authentication
    def get(self):
      cwd = os.getcwd()
      folder = "UPLOAD"
      path = os.path.join(cwd, folder)
      print(path)
      user_id=request.args.get('user_id')
      comment_id=request.args.get('comment_id')
      query_id=request.args.get('query_id')
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
          else:
            file=comment_check.file_path
            if file:
                return send_from_directory(path,file)
            return
      elif query_id:
        query_check = Queries.query.filter_by(id=query_id).first()
        if not query_check:
            app.logger.info('query not found')
            return jsonify(status=400, message="query not found")
        else:
            file=query_check.file_path
            if file:
                return send_from_directory(path,file)
            return

# class upload(Resource):
#     def post(self):
#         # file_print()
#         UPLOAD_FOLDER = '/home/sharonkamalkothapalli/uploads'
#         # ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
#         app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#         file = request.files.get('file')
#         user_id = request.form['user_id']
#         comment_id = request.form['comment_id']
#         # file=request.files('file')
#         print(file)
#         if not file:
#             app.logger.info('file required')
#             return jsonify(status=400, message="file required")
#         if file:
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             path = f'{UPLOAD_FOLDER}/{filename}'
#             print(path)
#             today = datetime.now()
#             date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#             user_id, comment_id, filename, path, today, today
#             newfile = Files(user_id, comment_id, filename, path, today, today, filename, path, user_id, comment_id, date_time_obj, date_time_obj)
#             db.session.add(newfile)
#             db.session.commit()
#         app.logger.info('file uploaded successfully')
#         return jsonify(status=200, message="file uploaded successfully")
#
#     def get(self):
#         data = request.get_json() or {}
#         UPLOAD_FOLDER = '/home/sharonkamalkothapalli/uploads'
#         app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#         # file = request.files['file']
#         file = data.get('file_id')
#         check_file = Files.query.filter_by(id=file).first()
#         if not file:
#             app.logger.info('file required')
#             return jsonify(status=400, message="file required")
#         if not check_file:
#             app.logger.info('file required')
#             return jsonify(status=400, message="file required")
#         if file:
#             # filename = secure_filename(file)
#             # print(filename)
#             return send_from_directory(app.config["UPLOAD_FOLDER"], check_file.name)
#
#
# def upload_file(user_id, comment_id_obj, file):
#     UPLOAD_FOLDER = '/home/sharonkamalkothapalli/uploads'
#     # ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
#     app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#     comment_id = comment_id_obj.id
#     for itr in file:
#         if itr:
#             filename = secure_filename(itr.filename)
#             itr.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             path = f'{UPLOAD_FOLDER}/{filename}'
#             print(path)
#             today = datetime.now()
#             newfile = Files(user_id, comment_id, filename, path, today, today)
#             db.session.add(newfile)
#             db.session.commit()
#     app.logger.info('file uploaded successfully')
#     return jsonify(status=200, message="file uploaded successfully")
#
#
# def retrive_file(self):
#     UPLOAD_FOLDER = '/home/sharonkamalkothapalli/uploads'
#     app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#     # file = request.files['file']
#     file = request.files.getlist('file[]')
#     if not file:
#         app.logger.info('file required')
#         return jsonify(status=400, message="file required")
#     for itr in file:
#         if itr:
#             filename = secure_filename(itr.filename)
#             print(filename)
#             return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

