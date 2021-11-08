# from flask import jsonify, request
# from sqlalchemy.sql import or_
# from flask_restplus import Resource
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
# from .models import User, Technologies, Queries, Comments
# from app import app, db
# from sqlalchemy import or_, and_, desc
# import re, ast
# from app.authentication import encode_auth_token, authentication
# from .serilalizer import query_serializer, comments_serializer, user_serializer, replace_with_ids, technology_serializer
# from .pagination import get_paginated_list
#
# class Login(Resource):
#     def post(self):
#         data = request.get_json() or {}
#         if not data:
#             app.logger.info("No input(s)")
#             return jsonify(status=400, message="No input(s)")
#         email = data.get("email")
#         mobile = data.get("mobile")
#         password = data.get('password')
#         if not ((email or mobile) and password):
#             app.logger.info("email or mobile and password are required")
#             return jsonify(status=400, message="email or mobile and password are required")
#         user = db.session.query(User).filter(or_(User.email == email, User.mobile == mobile)).first()
#         if user:
#             if check_password_hash(user.password, password):
#                 token = encode_auth_token(user)
#                 app.logger.info(token)
#                 response = user_serializer(user)
#                 app.logger.info(f'{user.name} Logged in successfully')
#                 return jsonify(status=200, data=response, message="Logged in successfully", token=token.decode('UTF-8'))
#             else:
#                 app.logger.info(f"{user.name} Incorrect password")
#                 return jsonify(status=404, messsage="Incorrect password")
#         else:
#             app.logger.info(f"user not found")
#             return jsonify(status=404, message="user not found")
#
#
# class Logout(Resource):
#     def post(self):
#         app.logger.info("Logged out successfully")
#         return jsonify(status=200, message="Logged out successfully")
#
#     def get(self):
#         app.logger.info("Logged out successfully")
#         return jsonify(status=200, message="Logged out successfully")
#
#
# class Register(Resource):
#     def post(self):
#         data = request.get_json()
#         name = data.get('name')
#         email = data.get('email')
#         mobile = data.get('mobile')
#         list_of_tech = data.get('technology')
#         password = data.get("password")
#
#         # check all data exists or not
#         if not (name and email and mobile and list_of_tech and password):
#             msg = 'name, email, mobile, technology and password are required fields'
#         # check valid email
#         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
#             msg = 'Invalid email address'
#         elif not (re.match(r'[0-9]+', mobile) and len(mobile) == 10):
#             msg = 'Invalid phone number'
#         # check valid name
#         elif not re.match(r'[A-Za-z0-9]+', name):
#             msg = 'Name must contain only characters and numbers'
#         elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$', password):
#             msg = 'Password should contain min 8 characters, a special character, Uppercase, lowercase and a number'
#         # check user already exist
#         else:
#             try:
#                 user = db.session.query(User).filter(or_(User.email == email,
#                                                          User.mobile == mobile,
#                                                          User.name == name)).first()
#                 if user:
#                     msg = 'User already exist'
#                 else:
#                     ids_list = f"{replace_with_ids(list_of_tech)}"
#
#                     print(ids_list)
#
#                     # technology = ast.literal_eval(technology)
#                     today = datetime.now()
#                     date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#                     print(date_time_obj)
#                     password = generate_password_hash(password, method='sha256')
#                     user = User(name, email, mobile, ids_list, password, date_time_obj, date_time_obj)
#
#                     db.session.add(user)
#                     db.session.commit()
#
#                     response = {"name": name, "email": email, "mobile": mobile, "technology": list_of_tech}
#                     app.logger.info(f'{user.name} Registered successfully')
#                     return jsonify(status=200, data=response, message="Registered successfully")
#             except:
#                 app.logger.info("Database connection not established")
#                 return jsonify(status=404, message="Database connection not established")
#         app.logger.info(msg)
#         return jsonify(status=400, message=msg)
#
#
# class UpdatePassword(Resource):
#     @authentication
#     def put(self):
#         data = request.get_json() or {}
#         email = data.get("email")
#         mobile = data.get("mobile")
#         old_password = data.get("old_password")
#         new_password = data.get("new_password")
#         confirm_new_password = data.get("confirm_new_password")
#
#         if not ((email or mobile) and (old_password and new_password and confirm_new_password)):
#             app.logger.info(f'email (or) mobile , old_password, new_password and confirm_new_password required')
#             return jsonify(status=400,
#                            message="email (or) mobile , old_password, new_password and confirm_new_password required")
#         try:
#             user = db.session.query(User).filter(or_(User.email == email, User.mobile == data.get("mobile"))).first()
#             if user:
#
#                 if check_password_hash(user.password, data.get('old_password')):
#                     if new_password == confirm_new_password:
#                         if new_password == old_password:
#                             app.logger.info("New password and old password should not be same")
#                             return jsonify(status=400, message="New password and old password should not be same")
#                         if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$',
#                                         new_password):
#                             app.logger.info(
#                                 "Password should contain min 8 characters, a special character, Uppercase, lowercase and a number")
#                             return jsonify(status=400,
#                                            message='Password should contain min 8 characters, a special character, Uppercase, lowercase and a number')
#                         user.password = generate_password_hash(new_password, method='sha256')
#                         db.session.commit()
#                         app.logger.info(f'{user.name} Password updated successfully')
#                         return jsonify(status=200, message="Password updated successfully")
#                     else:
#                         app.logger.info(f'{user.name} New password and confirm new password doesnt match')
#                         return jsonify(status=200, message="New password and confirm new password doesn't match")
#                 else:
#                     app.logger.info(f"{user.name} Incorrect old password")
#                     return jsonify(status=404, message="Incorrect old password")
#             else:
#                 app.logger.info("User not found")
#                 return jsonify(status=404, message="User not found")
#         except:
#             app.logger.info("Unknown database")
#             return jsonify(status=404, message="Unknown database")
#
#
# class ForgotPassword(Resource):
#     def post(self):
#         data = request.get_json() or {}
#         email = data.get("email")
#         mobile = data.get("mobile")
#         new_password = data.get("new_password")
#         confirm_new_password = data.get("confirm_new_password")
#         if not (email and mobile and new_password and confirm_new_password):
#             app.logger.info("email,mobile,new_password and confirm_new_password feilds are required")
#             return jsonify(status=400, message="email,mobile,new_password and confirm_new_password feilds are required")
#         else:
#             try:
#                 user = db.session.query(User).filter(and_(User.email == email, User.mobile == mobile)).first()
#                 if user:
#                     if new_password == confirm_new_password:
#                         if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$',
#                                         new_password):
#                             app.logger.info(
#                                 "Password should contain min 8 characters, a special character, Uppercase, lowercase and a number")
#                             return jsonify(status=400,
#                                            message='Password should contain min 8 characters, a special character, Uppercase, lowercase and a number')
#                         today = datetime.now()
#                         date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#                         user.updated_at = date_time_obj
#                         user.password = generate_password_hash(data.get('new_password'), method='sha256')
#                         db.session.commit()
#                         app.logger.info(f'{user.name} password changed  successfully')
#                         return jsonify(status=200, message="password changed  successfully")
#                     app.logger.info(f'{user.name} new_password and confirm_new_password are not same')
#                     return jsonify(status=400, message="new_password and confirm_new_password are not same")
#                 app.logger.info("cannot change password")
#                 return jsonify(status=400, message="cannot change password")
#             except:
#                 app.logger.info("database error")
#                 return jsonify(status=400, message="database error")
#

# class AddTechnologies(Resource):
#     @authentication
#     def post(self):
#         data = request.get_json() or {}
#         user_id = data.get('user_id')
#         technologies = data.get('technologies')
#         if not (user_id and technologies):
#             app.logger.info("User_id and technologies are required")
#             return jsonify(status=404, message="User_id and technologies are required")
#         check_user = User.query.filter_by(id=user_id).first()
#         if not check_user:
#             app.logger.info("User not found")
#             return jsonify(status=400, message="User not found")
#         if not (check_user.roles == 2 or check_user.roles == 3):
#             app.logger.info("User not allowed to add technologies")
#             return jsonify(status=404, message="User not allowed to add technologies")
#         for itr in technologies:
#             check_tech_exist = Technologies.query.filter_by(name=itr).first()
#             if check_tech_exist:
#                 app.logger.info(f"{itr} technology already exists")
#                 return jsonify(status=400, message=f"{itr} technology already exists")
#         today = datetime.now()
#         date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#         for itr in technologies:
#             tech = Technologies(itr, date_time_obj, date_time_obj)
#             db.session.add(tech)
#             db.session.commit()
#         return jsonify(status=200, message="added successfully")
#
#     def get(self):
#         t_list = []
#         technology_obj = db.session.query(Technologies).order_by(Technologies.updated_at)
#
#         if not technology_obj:
#             app.logger.info("No Technologies in DB")
#             return jsonify(status=404, message="No Technologies in DB")
#
#         for itr in technology_obj:
#             dt = technology_serializer(itr)
#             t_list.append(dt)
#
#         if not t_list:
#             app.logger.info("No Technologies in DB")
#             return jsonify(status=404, message="No Technologies in DB")
#
#         app.logger.info("Return Technologies data")
#         return jsonify(status=200, data=t_list, message="Returning Technologies data")
#     @authentication
#     def delete(self):
#         data = request.get_json() or {}
#         if not data:
#             app.logger.info("No input(s)")
#             return jsonify(status=400, message="No input(s)")
#         tech_id = data.get('tech_id')
#         user_id = data.get('user_id')
#         tech_check = db.session.query(Technologies).filter_by(id=tech_id).first()
#         user_check = db.session.query(User).filter_by(id=user_id).first()
#
#         if not (tech_id and user_id):
#             app.logger.info("Query id, user_id required to delete")
#             return jsonify(status=404, message="Query id, user_id required to delete")
#         if not user_check:
#             app.logger.info("User not found")
#             return jsonify(status=400, message="User not found")
#         if tech_check:
#             if (user_check.roles != 1):
#                 db.session.delete(tech_check)
#                 db.session.commit()
#                 app.logger.info("Query deleted successfully")
#                 return jsonify(status=200, message="Query deleted successfully")
#             app.logger.info("User not allowed to delete")
#             return jsonify(status=404, message="User not allowed to delete")
#
#         app.logger.info("Technology not found")
#         return jsonify(status=400, message="Technology not found")
#
#
# class QueriesClass(Resource):
#     @authentication
#     def post(self):
#         data = request.get_json() or {}
#         user_id = data.get('user_id')
#         user_check = db.session.query(User).filter_by(id=user_id).first()
#         tech = data.get('technology')
#         tech_check = db.session.query(Technologies).filter_by(name=tech).first()
#         title = data.get('title')
#         description = data.get('description')
#
#         if not (title and description and tech and user_id):
#             app.logger.info("title, description, user_id and technology are required")
#             return jsonify(status=200, message="title, description, user_id and technology are required")
#         if not user_check:
#             app.logger.info("user not found")
#             return jsonify(status=400, message="user not found")
#         if not tech_check:
#             app.logger.info("technology not found")
#             return jsonify(status=400, message="technology not found")
#
#         query_insertion = db.session.query(Queries).filter(or_(Queries.title == title,
#                                                                Queries.description == description)).first()
#
#         if query_insertion:
#             if query_insertion.title == title:
#                 app.logger.info("Data already exist")
#                 return jsonify(status=200, message="Data already exist")
#
#         today = datetime.now()
#         date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#         try:
#             question = Queries(user_id, title, description, tech_check.id, date_time_obj, date_time_obj)
#             db.session.add(question)
#             db.session.commit()
#         except:
#             app.logger.info("user not found")
#             return jsonify(status=400, message="user not found")
#         app.logger.info("Query inserted successfully")
#         response = query_serializer(question)
#         return jsonify(status=200, data=response, message="Query inserted successfully")
#
#     @authentication
#     def put(self):
#         data = request.get_json() or {}
#         query_id = data.get('query_id')
#         user_id = data.get('user_id')
#         user_check = db.session.query(User).filter_by(id=user_id).first()
#         tech = data.get('technology')
#         tech_check = db.session.query(Technologies).filter_by(name=tech).first()
#         query_check = db.session.query(Queries).filter_by(id=query_id).first()
#         # except:
#         #     app.logger.info("(query_id/user_id/tech_list) not found")
#         #     return jsonify(status=400, message="(query_id/user_id/tech_list) not found")
#         title = data.get('title')
#         description = data.get('description')
#
#         if not (query_id and user_id and title and description and tech):
#             app.logger.info("Query id , User id , title , description, technology are required fields")
#             return jsonify(status=404,
#                            message="Query id , User id , title , description, technology are required fields")
#         if not user_check:
#             app.logger.info("User not found")
#             return jsonify(status=400, message="User not found")
#         if not tech_check:
#             app.logger.info("Technology not found")
#             return jsonify(status=400, message="Technology not found")
#         if query_check:
#             if ((query_check.u_id == user_id) or (user_check.roles != 1)):
#                 query_check.title = title
#                 query_check.description = description
#                 query_check.t_id = tech_check.id
#                 today = datetime.now()
#                 date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#                 query_check.updated_at = date_time_obj
#                 db.session.commit()
#                 response = {"query_id": query_check.id, "title": query_check.title,
#                             "description": query_check.description, "technology": tech}
#                 app.logger.info("Query changed successfully")
#                 return jsonify(status=200, data=response, message="Query changed successfully")
#             app.logger.info("User not allowed to edit")
#             return jsonify(status=404, message="User not allowed to edit")
#         app.logger.info("Query didn't found")
#         return jsonify(status=404, message="Query didn't found")
#
#     @authentication
#     def delete(self):
#         data = request.get_json() or {}
#         query_id = data.get('query_id')
#         user_id = data.get('user_id')
#         query_check = db.session.query(Queries).filter_by(id=query_id).first()
#         user_check = db.session.query(User).filter_by(id=user_id).first()
#
#         if not (query_id and user_id):
#             app.logger.info("Query id, user_id required to delete")
#             return jsonify(status=404, message="Query id, user_id required to delete")
#         if not user_check:
#             app.logger.info("user not found")
#             return jsonify(status=404, message="user not found")
#         if query_check:
#             if ((query_check.u_id == user_id) or (user_check.roles != 1)):
#                 delete_comment = db.session.query(Comments).filter_by(q_id=query_id).all()
#                 if delete_comment:
#                     for itr in delete_comment:
#                         db.session.delete(itr)
#                         db.session.commit()
#                 else:
#                     app.logger.info("No comments for this query, deleting this query ")
#                 db.session.delete(query_check)
#                 db.session.commit()
#                 app.logger.info("Query deleted successfully")
#                 return jsonify(status=200, message="Query deleted successfully")
#             app.logger.info("User not allowed to delete")
#             return jsonify(status=404, message="User not allowed to delete")
#
#         app.logger.info("Query not found")
#         return jsonify(status=400, message="Query not found")
#
#     def get(self):  # send all the comments based on comment_id or u_id or q_id or send all
#
#         order_by_query_obj = db.session.query(Queries).order_by(Queries.updated_at)
#         if not order_by_query_obj:
#             app.logger.info("No Queries in DB")
#             return jsonify(status=404, message="No Queries in DB")
#
#         c_list = []
#         for itr in order_by_query_obj:
#             dt = query_serializer(itr)
#             c_list.append(dt)
#
#         app.logger.info("Return queries data")
#         return jsonify(status=200, data=get_paginated_list(c_list, '/query', start=request.args.get('start', 1),
#                                                            limit=request.args.get('limit', 3)),
#                        message="Returning queries data")
#
#
# class CommentClass(Resource):
#     @authentication
#     def post(self):
#         data = request.get_json() or {}
#         query_id = data.get('query_id')
#         user_id = data.get('user_id')
#         queries_check = db.session.query(Queries).filter_by(id=query_id).first()
#         user_check = db.session.query(User).filter_by(id=user_id).first()
#         comment = data.get('comment')
#         if not (query_id and user_id and comment):
#             app.logger.info("query_id,user_id and comment are required")
#             return jsonify(status=400, message="query_id,user_id and comment are required")
#         if not user_check:
#             app.logger.info("user not found")
#             return jsonify(status=400, message="user not found")
#         if not queries_check:
#             app.logger.info("query not found")
#             return jsonify(status=400, message="query not found")
#         today = datetime.now()
#         date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#         comm = Comments(user_id, query_id, comment, date_time_obj, date_time_obj)
#         db.session.add(comm)
#         db.session.commit()
#         app.logger.info("comment inserterd succesfully")
#         return jsonify(status=200, message="comment inserterd succesfully")
#
#     @authentication
#     def put(self):
#         data = request.get_json() or {}
#         query_id = data.get('query_id')
#         user_id = data.get('user_id')
#         comment_id = data.get('comment_id')
#         query_check=db.session.query(Queries).filter_by(id=query_id).first()
#         edit_comment_by_id = db.session.query(Comments).filter_by(id=comment_id).first()
#         check_user = db.session.query(User).filter_by(id=user_id).first()
#         check_queries_auth = db.session.query(Queries).filter_by(u_id=user_id).first()
#         edited_comment = data.get('edited_comment')
#         if not (query_id and user_id and edited_comment and comment_id):
#             app.logger.info("query_id , user_id , edited_comment and comment_id are required fields")
#             return jsonify(status=400, message="query_id , user_id , edited_comment and comment_id are required fields")
#         if not check_user:
#             app.logger.info("user not found")
#             return jsonify(status=404, message="user not found")
#         if not query_check:
#             app.logger.info("query not found")
#             return jsonify(status=404, message="query not found")
#         if not (check_queries_auth or check_user != 1):
#             app.logger.info("cant edit comment")
#             return jsonify(status=404, message="cant edit comment")
#         if not edit_comment_by_id:
#             app.logger.info("Comment not found")
#             return jsonify(status=400, message="Comment not found")
#         if not ((edit_comment_by_id.u_id == user_id) or check_user.roles != 1):
#             app.logger.info("User not allowed to edit")
#             return jsonify(status=404, message="User not allowed to edit")
#         edit_comment_by_id.msg = edited_comment
#         db.session.commit()
#         app.logger.info("Comment edited")
#         return jsonify(status=200, message="Comment edited",
#                        data={"query_id": query_id, "comment_id": comment_id, "edited_comment": edited_comment})
#
#     @authentication
#     def delete(self):
#         data = request.get_json() or {}
#         query_id = data.get('query_id')
#         user_id = data.get('user_id')
#         comment_id = data.get('comment_id')
#         if not (query_id and user_id and comment_id):
#             app.logger.info("Query_id , user_id and comment_id are required")
#             return jsonify(status=200, message="Query_id , user_id and comment_id are required")
#         query_check = db.session.query(Queries).filter_by(id=query_id).first()
#         user_check = db.session.query(User).filter_by(id=user_id).first()
#         if not user_check:
#             app.logger.info("User not found")
#             return jsonify(status=400, message="User not found")
#
#         if not query_check:
#             app.logger.info("Query not found")
#             return jsonify(status=400, message="Query not found")
#         comment_check = db.session.query(Comments).filter_by(id=comment_id).first()
#         if not comment_check:
#             app.logger.info("Comment not found")
#             return jsonify(status=400, message="Comment not found")
#         if not ((comment_check.u_id == user_id) or user_check.roles != 1):
#             app.logger.info("User not allowed to delete")
#             return jsonify(status=404, message="User not allowed to delete")
#         db.session.delete(comment_check)
#         db.session.commit()
#         app.logger.info("Comment deleted successfully")
#         return jsonify(status=200, message="Comment deleted successfully")
#
#     def get(self):  # send all the comments based on comment_id or u_id or q_id or send all
#
#         order_by_comment_obj = db.session.query(Comments).order_by(Comments.updated_at)
#         if not order_by_comment_obj:
#             app.logger.info("No Comments in DB")
#             return jsonify(status=404, message="No comments in DB")
#
#         c_list = []
#         for itr in order_by_comment_obj:
#             dt = comments_serializer(itr)
#             c_list.append(dt)
#
#         app.logger.info("Return comments data")
#         return jsonify(status=200, data=get_paginated_list(c_list, '/comment', start=request.args.get('start', 1),
#                                                            limit=request.args.get('limit', 3)),
#                        message="Returning comments data")
#
#
# class UserProfile(Resource):
#     def get(self):
#         data=request.get_json() or {}
#         user_id=data.get('user_id')
#         if not user_id:
#             app.logger.info("user_id required")
#             return jsonify(status=400,message="user_id required")
#         user_data=db.session.query(User).filter_by(id=user_id).first()
#         if not user_data:
#             app.logger.info("user not found")
#             return jsonify(status=400, message="user not found")
#         return jsonify(status=200,data=user_serializer(user_data),message="user data")
#
#     def put(self):
#         data = request.get_json() or {}
#         try:
#             user_id=data.get('user_id')
#             user_update = User.query.filter_by(id = user_id).first()
#         except:
#             app.logger.info("User not found")
#             return jsonify(status=404, message="user not found")
#         name = data.get('name')
#         technology = data.get('technology')
#
#         if not (name  and technology and user_id):
#             app.logger.info("name,technology and user_id are required")
#             return jsonify(status=400, message="name,technology and user_id are required")
#
#         elif not re.match(r'[A-Za-z0-9]+', name):
#             msg = 'name must contain only characters and numbers'
#             app.logger.info(msg)
#             return jsonify(status=404, message=msg)
#         else:
#             if user_update:
#                 if not user_update.name == name:
#                     user_update.name = name
#                 else:
#                  app.logger.info("new name should be taken")
#                  return jsonify(status=400,message="new name should be taken")
#                 tech_list=[]
#                 for itr in technology:
#                     tech_check=Technologies.query.filter_by(name=itr).first()
#                     if tech_check:
#                         tech_list.append(tech_check.id)
#                 user_update.technology=f"{tech_list}"
#                 today = datetime.now()
#                 user_update.date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#                 db.session.commit()
#                 response = {"name": user_update.name, "technology": technology}
#                 app.logger.info(f'{user_update.name} Updated successfully')
#                 return jsonify(status=200, data=response, message="updated Successfully")
#
#
# class UserStatus(Resource):
#     @authentication
#     def put(self):
#         data = request.get_json() or {}
#         if not data:
#             app.logger.info("No input(s)")
#             return jsonify(status=400, message="No input(s)")
#         user_id = data.get('user_id')
#         change_user_id = data.get('change_user_id')
#         change_user_role = data.get('change_user_role')
#         if not (change_user_id and user_id and change_user_role):
#             app.logger.info("change_user_id and user id and change_user_role are required fields")
#             return jsonify(status=404, message="change_user_id and user id and change_user_role are required fields")
#         user_check = db.session.query(User).filter_by(id=user_id).first()
#         if not user_check:
#             app.logger.info("User not found")
#             return jsonify(status=400, message="User not found")
#         change_user_role = db.session.query(User).filter_by(id=change_user_id).first()
#         if not change_user_role:
#             app.logger.info("User you wanted to change role not found")
#             return jsonify(status=400, message="User you wanted to change role not found")
#
#         if user_check.roles == 2:
#             change_user_role.roles = 2
#             today = datetime.now()
#             date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#             change_user_role.updated_at = date_time_obj
#             db.session.commit()
#             app.logger.info(f"{change_user_role.name} role changed successfully")
#             return jsonify(status=200, message=f"{change_user_role.name} role changed successfully")
#         app.logger.info("User not allowed to perform this action")
#         return jsonify(status=404, message="User not allowed to perform this action")
#
#     @authentication
#     def delete(self):
#         data = request.get_json() or {}
#         if not data:
#             app.logger.info("No input(s)")
#             return jsonify(status=400, message="No input(s)")
#         user_id = data.get('user_id')
#         delete_user = data.get('delete_user_id')
#         if not (delete_user and user_id):
#             app.logger.info("delete_user_id and User id are required fields")
#             return jsonify(status=404, message="delete_user_id and User id are required fields")
#         user_check = db.session.query(User).filter_by(id=user_id).first()
#         if not user_check:
#             app.logger.info("User not found")
#             return jsonify(status=400, message="User not found")
#         delete_user = db.session.query(User).filter_by(id=delete_user).first()
#         if not delete_user:
#             app.logger.info("User wanted to delete not found")
#             return jsonify(status=400, message="User wanted to delete not found")
#
#         if user_check.roles != 1:
#             delete_user.roles = 0
#             today = datetime.now()
#             date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
#             delete_user.updated_at = date_time_obj
#             db.session.commit()
#             app.logger.info(f"{delete_user} disabled successfully")
#             return jsonify(status=200, message=f"{delete_user} disabled successfully")
#         app.logger.info("User not allowed to perform this action")
#         return jsonify(status=404, message="User not allowed to perform this action")
#

# class GetCommentByQuery(Resource):
#     def get(self, query_id):
#         comment_obj = db.session.query(Comments).filter_by(id=query_id).all()
#         if not comment_obj:
#             app.logger.info("No Comments found")
#             return jsonify(status=404, message="No comments found")
#         comment_list = []
#         for itr in comment_obj:
#             dt = comments_serializer(itr)
#             comment_list.append(dt)
#         app.logger.info("Return comments data")
#         return jsonify(status=200,
#                        data=get_paginated_list(comment_list, '/getcomments', start=request.args.get('start', 1),
#                                                limit=request.args.get('limit', 3)), message="Returning queries data")
#
#
# class GetCommentsUserId(Resource):
#
#     def get(self, user_id):  # send all the comments based on user_id
#         try:
#             c_list = []
#             comments_obj = db.session.query(Comments).filter_by(u_id=user_id).all()
#
#             if not comments_obj:
#                 app.logger.info("No Comments in DB")
#                 return jsonify(status=404, message="No comments in DB")
#
#             for itr in comments_obj:
#                 if itr.u_id == user_id:
#                     dt = comments_serializer(itr)
#                     c_list.append(dt)
#
#             if not c_list:
#                 app.logger.info("No comments in DB")
#                 return jsonify(status=404, message="No comments found")
#             user_id_str = str(user_id)
#             page = '/getcomments/user/' + user_id_str
#
#             app.logger.info("Return comments data")
#             return jsonify(status=200, data=get_paginated_list(c_list, page, start=request.args.get('start', 1),
#                                                                limit=request.args.get('limit', 3)),
#                            message="Returning queries data")
#
#         except:
#             return jsonify(status=400, message="No inputs found")
#
#
# class GetCommentsByUserId(Resource):
#
#     def get(self, user_id):  # send all the comments based on user_id
#         try:
#             c_list = []
#             comments_obj = db.session.query(Comments).filter_by(u_id=user_id).all()
#
#             if not comments_obj:
#                 app.logger.info("No Comments in DB")
#                 return jsonify(status=404, message="No comments in DB")
#
#             for itr in comments_obj:
#                 if itr.u_id == user_id:
#                     dt = comments_serializer(itr)
#                     c_list.append(dt)
#
#             # if not c_list:
#             #     app.logger.info("No comments in DB")
#             #     return jsonify(status=404, message="No comments found")
#             user_id_str = str(user_id)
#             page = '/getcomments/user/' + user_id_str
#
#             app.logger.info("Return comments data")
#             return jsonify(status=200, data=get_paginated_list(c_list, page, start=request.args.get('start', 1),
#                                                                limit=request.args.get('limit', 3)),
#                            message="Returning queries data")
#
#         except:
#             return jsonify(status=400, message="No inputs found")
#
#
# # class GetCommentBycommentId(Resource):
# #     def get(self,comment_id): #send all the comments based on user_id
# #         try:
# #             c_list = []
# #             comments_obj = db.session.query(Comments).filter_by(id=comment_id).first()
#
# #             if not comments_obj:
# #                 app.logger.info("No Comments in DB")
# #                 return jsonify(status=404, message="No comments in DB")
#
# #             for itr in comments_obj:
# #                 if itr.u_id == user_id:
# #                     dt = comments_serializer(itr)
# #                     c_list.append(dt)
#
# #             if not c_list:
# #                 app.logger.info("No comments in DB")
# #                 return jsonify(status=404, message="No comments found")
# #             user_id_str=str(user_id)
# #             page = '/getcomments/user/'+user_id_str
#
# #             app.logger.info("Return comments data")
# #             return jsonify(status=200, data=get_paginated_list(c_list, page, start=request.args.get('start', 1),
# #                                           limit=request.args.get('limit', 3)), message="Returning queries data")
#
# #         except:
# #             return jsonify(status=400, message="No inputs found")
#
# class GetQueryByUserId(Resource):
#     def get(self, user_id):
#         queries_obj = db.session.query(Queries).filter_by(u_id=user_id).all()
#         if not queries_obj:
#             app.logger.info("No queries found")
#             return jsonify(status=404, message="No queries found")
#         queries_list = []
#         for itr in queries_obj:
#             dt = query_serializer(itr)
#             queries_list.append(dt)
#         user_id_str = str(user_id)
#         page = '/getqueries/user/' + user_id_str
#         app.logger.info("Returning queries data")
#         return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
#                                                            limit=request.args.get('limit', 3)),
#                        message="Returning queries data")
#
#
# class GetQueryByTitle(Resource):
#     def get(self, title):
#         queries_obj = db.session.query(Queries).filter_by(title=title).first()
#         if not queries_obj:
#             app.logger.info("No queries found")
#             return jsonify(status=404, message="No queries found")
#         queries_list = []
#         page = '/getqueries/user/' + title
#         app.logger.info("Returning query data")
#         return jsonify(status=200,
#                        data=get_paginted_list(query_serializer(queries_obj), page, start=request.args.get('start', 1),
#                                                limit=request.args.get('limit', 3)), message="Returning queries data")
#
#
# class GetQueryByTechnology(Resource):
#     def get(self, technology):
#         tech_obj = db.session.query(Technologies).filter_by(name=technology).first()
#         if not tech_obj:
#             app.logger.info("technology not found")
#             return jsonify(status=404, message="technology not found")
#
#         queries_obj = db.session.query(Queries).filter_by(t_id=tech_obj.id).all()
#         if not queries_obj:
#             app.logger.info("No queries found")
#             return jsonify(status=404, message="No queries found")
#         queries_list = []
#         for itr in queries_obj:
#             dt = query_serializer(itr)
#             queries_list.append(dt)
#         page = '/getqueries/technology/' + technology
#         app.logger.info("Returning queries data")
#         return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
#                                                            limit=request.args.get('limit', 3)),
#                        message="Returning queries data")
#
#
# class Likes(Resource):
#     def post(self):
#         data = request.get_json()
#         comment_id = data.get('comment_id')
#
#         comment_obj = db.session.query(Comments).filter_by(id=comment_id).first()
#         if not comment_obj:
#             app.logger.info("Record not found")
#             return jsonify(status=400, message="Record not found")
#         list=[]
#         for itr in str(comment_obj).str(q_id).u_id:
#             list.append(itr)
#             print(len(list))
#         for i in range(len(list)-1):
#             for j in range(len(list)-1):
#                if list[i] == list[j]:
#                   print("1111")
#                   return jsonify("already liked")
#                else:
#                  print("2222")
#                  if comment_obj.like_count == None:
#                    comment_obj.like_count = 1
#                  else:
#                   comment_obj.like_count = comment_obj.like_count + 1
#                db.session.commit()
#                app.logger.info("Liked a comment")
#                return jsonify(status=200, message="Liked Successfully!")
#
#
# class DisLikes(Resource):
#     def post(self):
#         data = request.get_json()
#         comment_id = data.get('comment_id')
#
#         comment_obj = db.session.query(Comments).filter_by(id=comment_id).first()
#         if not comment_obj:
#             app.logger.info("Record not found")
#             return jsonify(status=400, message="Record not found")
#
#         if comment_obj.dislike_count == None:
#             comment_obj.dislike_count = 1
#         else:
#             comment_obj.dislike_count = comment_obj.dislike_count + 1
#         db.session.commit()
#         app.logger.info("DisLiked Successfully!")
#         return jsonify(status=200, message="DisLiked Successfully!")