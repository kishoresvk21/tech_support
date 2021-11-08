from flask import jsonify, request
from sqlalchemy.sql import or_
from flask_restplus import Resource
from datetime import datetime
from app.user.models.models import Queries,User,Technologies,Comments,SavedQueries,Support
from app import app, db
from sqlalchemy import or_, and_, desc
import re, ast
from app.authentication import encode_auth_token, authentication,get_user_id,is_active
from app.user.serilalizer.serilalizer import ticket_serializer
from app.user.pagination.pagination import get_paginated_list
from app.utils.form_validations import title_validator,description_validator
from app.user.fileupload.file_upload import upload_file
from app.utils.smtpmail import mail_for_support_ticket,mail_for_updating_support_ticket,mail_for_cancelling_support_ticket

class SupportTicket(Resource):
    def post(self):
        try:
          user_id=request.form['user_id']
          title=request.form['title']
          problem=request.form['problem']
        except:
            app.logger.info("user_id,title and problem are required")
            return jsonify(status=400,message="user_id,title and problem are required")
        file = request.files.get('file')

        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=404, message="user disabled temporarily")

        if not title_validator(title):
            app.logger.info("Invalid title length")
            return jsonify(status=400, message="Invalid title length")
        if not description_validator(problem):
            app.logger.info("Invalid problem length")
            return jsonify(status=400, message="Invalid issue length")
        user_check = User.query.filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        if file:
            file_data = upload_file(self, file)
            filename = file_data[0]
            filepath = file_data[1]
        else:
            filepath = None
            filename = None
        status=True
        ticket = Support(user_id,title,problem,filename,filepath,status,date_time_obj, date_time_obj)
        db.session.add(ticket)
        db.session.commit()
        mail_for_support_ticket(ticket)
        app.logger.info("Ticket raised succesfully")
        return jsonify(status=200, message="Ticket raised succesfully")

    def put(self):
        new_file = request.files.get('file')
        try:
            title = request.form['title']
            user_id = request.form['user_id']
            support_ticket_id = request.form['support_ticket_id']
            description = request.form['description']
        except:
            app.logger.info("title, description, user_id and support_ticket_id are required")
            return jsonify(status=400, message="title, description, user_id and support_ticket_id are required")

        if not (support_ticket_id and user_id and title and description):
            app.logger.info("support_ticket_id, user_id, title and description are required fields")
            return jsonify(status=400, message="support_ticket_id, user_id, title and description are required fields")

        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=404, message="user disabled temporarily")

        if not title_validator(title):
            app.logger.info("Invalid title length")
            return jsonify(status=400, message="Invalid title length")

        if not description_validator(description):
            app.logger.info("Invalid description length")
            return jsonify(status=400, message="Invalid description length")

        user_check = User.query.filter_by(id=user_id).first()
        support_ticket_check = SupportTickets.query.filter_by(and_(Support.id==support_ticket_id,Support.u_id==user_id)).first()

        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        if not support_ticket_check:
            app.logger.info("Ticket not found")
            return jsonify(status=400, message="Ticket not found")
        if support_ticket_check:
            if support_ticket_check.status==True and support_ticket_check.userdelete==False:
                support_ticket_check.title = title
                support_ticket_check.description = description
                support_ticket_check.updated_at = datetime.now()
                if new_file:
                    file_data = upload_file(self, new_file)
                    new_file_name = file_data[0]
                    new_file_path = file_data[1]
                else:
                    new_file_name = None
                    new_file_path=None
                support_ticket_check.filename=new_file_name
                support_ticket_check.pathname=new_file_path
                db.session.commit()
                response = support_ticket_serializer(support_ticket_check)
                mail_for_updating_support_ticket(support_ticket_check)
                app.logger.info("Ticket updated successfully")
                return jsonify(status=200, data=response, message="Ticket updated successfully")
            app.logger.info("unable to update ticket")
            return jsonify(status=200, message="unable to update ticket")
        app.logger.info("Ticket not found")
        return jsonify(status=404, message="Ticket not found")

    def delete(self):
        data=request.get_json() or {}
        if not data:
            app.logger.info("enter user_id and ticket_id")
            return jsonify(status=200, message="enter user_id and ticket_id")
        user_id=data.get("user_id")
        ticket_id=data.get("ticket_id")
        if not user_id and ticket_id:
            app.logger.info("user_id and ticket_id are required")
            return jsonify(status=400, message="user_id and ticket_id are required")

        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=404, message="user disabled temporarily")

        user_check = User.query.filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        ticket_check=Support.query.filter_by(id=ticket_id).first()
        if not ticket_check:
            app.logger.info("ticket not found")
            return jsonify(status=400, message="ticket not found")
        delete_ticket=Support.query.filter(and_(Support.id==ticket_id,Support.u_id==user_id)).first()
        if delete_ticket:
         if delete_ticket.status==True :
            delete_ticket.userdelete=True
            db.session.add(delete_ticket)
            print("11")
            db.session.commit()
            mail_for_cancelling_support_ticket(delete_ticket)
            app.logger.info("Ticket cancelled succesfully")
            return jsonify(status=200, message="Ticket cancelled succesfully")
        app.logger.info("Unable to cancel ticket")
        return jsonify(status=200, message="Unable to cancel ticket")

    def get(self):

        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=404, message="user disabled temporarily")

        get_tickets = db.session.query(Support).filter().all()
        if not get_tickets:
            app.logger.info("no records found")
            return jsonify(status=400, message="no records found")
        s_list=[]
        for itr in get_tickets:
           if itr.userdelete == False:
             dt=ticket_serializer(itr)
             s_list.append(dt)
        if not s_list:
            app.logger.info("no records found")
            return jsonify(status=400, message="no records found")
        app.logger.info("returning tickets data")
        return jsonify(status=400, data=get_paginated_list(s_list, '/support', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="returning tickets data")

class GetTicketsByUserId(Resource):
    def get(self):
        user_id= request.args.get('user_id')
        if not user_id:
            app.logger.info("user_id required")
            return jsonify(status=404, message="user_id required")

        user_obj=db.session.query(User).filter_by(id=user_id).all()
        tickets_obj = db.session.query(Support).filter_by(u_id=user_id).all()

        active = is_active(user_id)
        if not active:
            app.logger.info("user disabled temporarily")
            return jsonify(status=404, message="user disabled temporarily")

        if not user_obj:
            app.logger.info("user not found")
            return jsonify(status=404, message="user not found")

        if not tickets_obj:
            app.logger.info("no records found")
            return jsonify(status=404, message="no records found")

        t_list=[]
        for itr in tickets_obj:
          if itr.userdelete==False:
             dt = ticket_serializer(itr)
             t_list.append(dt)

        if not t_list:
            app.logger.info("no records found")
            return jsonify(status=400, message="no records found")

        page = f"/getticketsbyuserid?user_id={user_id}"

        app.logger.info("Return tickets data")
        return jsonify(status=200, data = get_paginated_list(t_list, page, start=request.args.get('start', 1),
                    limit=request.args.get('limit', 3),with_params=True),message="Returning tickets data")
        # return jsonify(status=200, data=t_list,message="Returning tickets data")


