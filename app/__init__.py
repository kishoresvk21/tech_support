
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_restplus import Api
from flask_cors import CORS
from flask_migrate import Migrate

# from OpenSSL import SSL
# context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('server.crt')


app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"": {"origins": ""}, })
# app.secret_key="IIOOOOOWREE"
app.config['SECRET_KEY'] = 'rmijlkqqqawtre@1((11'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Mysql#123@localhost/tech_support'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
migrate=Migrate(app,db)
api = Api(app)

from app.user.queries.queries import UserGetQueryByTechnology,UserGetQueryByUserId, UserGetQueryByTechnology,UserQueries,\
    UserGetQueryByTitle,SaveQuery
from app.user.comments.comments import UserComment,UserGetCommentByQueryId,UserGetCommentsByuserId
from app.user.user.user import Register,Logout,UpdatePassword,ForgotPassword,UserProfile, UserStatus,Login
from app.user.opinion.like import Like,DisLike
from app.user.fileupload.file_upload import download
from app.user.support.support import SupportTicket,GetTicketsByUserId

from app.admin.technology.technology import Technology
from app.admin.comments.comments import AdminComment,AdminGetCommentsByUserId
from app.admin.queries.queries import AdminQueries,AdminGetQueryByUserId
from app.admin.queries.queries import Unanswered
from app.admin.users.users import AdminRoles,GetAllUsers,GetProfile,UserDelete,UserStatus,AdminForgotPassword,AdminLogin
from app.admin.dashboard.topusers import TopUsers
from app.admin.dashboard.admins import getadmins
from app.admin.dashboard.getusers import getusers,UserSearch
from app.admin.dashboard.filters import FilterRecord


# from app.utils.chatbot import Chat

api.add_resource(Login, "/login")
api.add_resource(Register,"/register")
api.add_resource(Logout,"/logout")
api.add_resource(UpdatePassword,"/changepassword")
api.add_resource(ForgotPassword,"/forgotpassword")
api.add_resource(UserQueries,"/query")
api.add_resource(UserComment,"/comment")
api.add_resource(UserProfile,"/profile")
api.add_resource(UserStatus,"/userstatuschange")
api.add_resource(UserGetCommentByQueryId,"/user/getcommentsbyqueryid")
api.add_resource(UserGetCommentsByuserId,"/user/getcommentsbyuserid")
api.add_resource(UserGetQueryByUserId,"/user/getqueriesbyuserid")
api.add_resource(UserGetQueryByTitle,"/user/getquerybytitle")
api.add_resource(UserGetQueryByTechnology,"/user/usergetquerybytechnology")
api.add_resource(Like,"/like")
api.add_resource(DisLike,"/dislike")
api.add_resource(download,"/download")
api.add_resource(SaveQuery,"/save")
api.add_resource(SupportTicket,"/support")
api.add_resource(GetTicketsByUserId,"/getticketsbyuserid")


api.add_resource(Technology,"/technology")
api.add_resource(AdminComment,"/admin/comments")
api.add_resource(AdminGetCommentsByUserId,"/admin/commentsbyuserid")
api.add_resource(AdminQueries,"/admin/queries")
api.add_resource(AdminGetQueryByUserId,"/admin/getquerybyuserid")
api.add_resource(TopUsers,"/topusers")
api.add_resource(FilterRecord,"/filter")
api.add_resource(getusers,"/getusers")
api.add_resource(getadmins,"/getadmins")
api.add_resource(Unanswered,"/unanswered")
api.add_resource(UserSearch,"/usersearch")
api.add_resource(AdminRoles,"/adminroles")


# api.add_resource(Chat,"/chat")