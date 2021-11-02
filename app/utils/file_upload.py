
# import os
# from flask import Flask, flash, request, redirect, url_for
# from werkzeug.utils import secure_filename
#
# UPLOAD_FOLDER = '/path/to/the/uploads'
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
#
# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # If the user does not select a file, the browser submits an
#         # empty file without a filename.
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('download_file', name=filename))

from flask import request,jsonify,send_from_directory
from werkzeug.utils import secure_filename
from app import app
from flask_restplus import Resource
from app.models_package.models import Files
from app import db
import os
from datetime import datetime
from app.utils.convert_file import file_print
class upload(Resource):
  def post(self):
   file_print()
   UPLOAD_FOLDER = '/home/krishnakishore/UPLOAD'
   # ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
   app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
   file = request.files.get('file')
   user_id=request.form['user_id']
   comment_id=request.form['comment_id']
   # file=request.files('file')
   print(file)
   if not file:
        app.logger.info('file required')
        return jsonify(status=400,message="file required")
   if file:
       filename = secure_filename(file.filename)
       file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
       path = f'{UPLOAD_FOLDER}/{filename}'
       print(path)
       today = datetime.now()
       date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
       newfile = Files(filename, path, user_id, comment_id, date_time_obj, date_time_obj)
       db.session.add(newfile)
       db.session.commit()
   app.logger.info('file uploded succesfully')
   return jsonify(status=200, message="file uploded succesfully")
  def get(self):
      data=request.get_json() or {}
      UPLOAD_FOLDER = '/home/krishnakishore/UPLOAD'
      app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
      # file = request.files['file']
      file = data.get('file_id')
      check_file=Files.query.filter_by(id=file).first()
      if not file:
          app.logger.info('file required')
          return jsonify(status=400, message="file required")
      if not check_file:
          app.logger.info('file required')
          return jsonify(status=400, message="file required")
      if file:
          # filename = secure_filename(file)
          # print(filename)
          return send_from_directory(app.config["UPLOAD_FOLDER"], check_file.name)

