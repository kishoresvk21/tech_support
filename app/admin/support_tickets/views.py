from flask_restplus import Resource
from app.authentication import authentication
from flask import request, jsonify
from app import app, db
from app.models_package.models import User, SupportTickets
from datetime import datetime
from app.pagination import get_paginated_list
from app.serializer import support_ticket_serializer
from app.authentication import is_active, get_user_id
from app.utils.form_validation import title_validator, description_validator
from app.utils.file_upload import upload_file
from app.utils.smtp_mail import mail_for_support_ticket


class AdminSupportTickets(Resource):
    @authentication
    def delete(self):
        user_id = get_user_id(self)
        active = is_active(user_id)
        if not active:
            app.logger.info("User disabled temporarily")
            return jsonify(status=404, message="User disabled temporarily")

        data = request.get_json() or {}
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")

        ticket_id = data.get('ticket_id')
        ticket_check = SupportTickets.query.filter_by(id=ticket_id).first()

        if not ticket_check:
            app.logger.info("No ticket found")
            return jsonify(status=404, message="No ticket found")

        ticket_check.status = False
        db.session.commit()
        mail_for_support_ticket(ticket_check)

        app.logger.info("Ticket is resolved")
        return jsonify(status=200, message="Ticket is resolved")

    @authentication
    def get(self):
        user_id = get_user_id(self)
        active = is_active(user_id)
        if not active:
            app.logger.info("User disabled temporarily")
            return jsonify(status=404, message="User disabled temporarily")

        get_tickets = SupportTickets.query.filter().all()
        print(get_tickets)
        if not get_tickets:
            app.logger.info("No records found")
            return jsonify(status=400, message="No records found")

        s_list = []
        for itr in get_tickets:
            if itr.userdelete is False:
                dt = support_ticket_serializer(itr)
                s_list.append(dt)

        if not s_list:
            app.logger.info("No records found")
            return jsonify(status=400, message="No records found")

        app.logger.info("Returning tickets data")
        return jsonify(status=400, data=get_paginated_list(s_list, '/admin/supportticket', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3), with_params=False),
                       message="returning tickets data")


class GetSupportTicketByTicketId(Resource):
    @authentication
    def get(self, ticket_id):
        user_id = get_user_id(self)
        active = is_active(user_id)
        if not active:
            app.logger.info("User disabled temporarily")
            return jsonify(status=404, message="User disabled temporarily")

        ticket_obj = SupportTickets.query.filter_by(id=ticket_id).first()
        if not ticket_obj:
            app.logger.info("No ticket found")
            return jsonify(status=404, message="No ticket found")

        if ticket_obj.userdelete is False:
            response = support_ticket_serializer(ticket_obj)
            app.logger.info("Returning ticket data")
            return jsonify(status=200, data=response, message="Returning ticket data")

        app.logger.info("Ticket is canceled")
        return jsonify(status=200, message="Ticket is canceled")
