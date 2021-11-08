import smtplib
import string
import random  # define the random module
from app.models_package.models import User
from app.utils.form_validation import password_validator
from app import app
from flask import jsonify


def generate_temp_password_and_check():
    S = 8  # number of characters in the string.
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    password = str(''.join(random.choices(alphabet, k=S)))
    if not password_validator(password):
        # print("Generated Password is not satisfying")
        print(password)
        return generate_temp_password_and_check()
    print(password)
    # print("Generated Password is satisfying")
    return password


def send_mail_to_reset_password(to, user_name):

    gmail_user = 'techblog.application@gmail.com'
    gmail_password = 'techblog@123'
    sent_from = gmail_user

    password = generate_temp_password_and_check()
    # subject = '[Tech-Blog] : Reset Password'
    subject = 'Forgot Password'
    body = "Hello " + f'{user_name}, ' + "\n\n" + \
           'Your account password with tech-blog has been changed and below are your login details.\n' +\
           "Email: " + f'{to}' + "\n" + \
           "Password: " + f'{password}' + "\n\n" + "Thanks,\nTech-Blog Group"

    email_text = f'Subject: {subject}' \
                 f'\n' \
                 f'\n' \
                 f'{body}'

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        # print("Email sent successfully!")
        return password
    except Exception as ex:
        print("Something went wrong….", ex)
        return "Error"


def mail_for_support_ticket(support_ticket_obj):
    gmail_user = 'techblog.application@gmail.com'
    gmail_password = 'techblog@123'
    sent_from = gmail_user

    subject = '[Tech-Blog] : Support Ticket '
    # subject = 'Support Ticket'
    user_name = User.query.filter_by(id=support_ticket_obj.u_id).first().name
    to = User.query.filter_by(id=support_ticket_obj.u_id).first().email

    if support_ticket_obj.status is True and support_ticket_obj.userdelete is False:
        body = "Hello " + f'{user_name}, ' + "\n\n" + \
               'Your ticket is been raised with the following ticket id.\n' + \
               "Ticket Id: " + f'{support_ticket_obj.id}' + "\n" + \
               'We will resolve your issue at the earliest.\n' + \
               "\n\n" + "Thanks,\nTech-Blog Group"

    elif (support_ticket_obj.status and support_ticket_obj.userdelete) is False:
        body = "Hello " + f'{user_name}, ' + "\n\n" + \
               'Your ticket with ticket id ' + f'{support_ticket_obj.id} ' + \
               'is resolved. Please check and feel free to contact us if you have any more further issues.\n' + \
               "\n\n" + "Thanks,\nTech-Blog Group"

    if (support_ticket_obj.status and support_ticket_obj.userdelete) is True:
        body = "Hello " + f'{user_name}, ' + "\n\n" + \
               'Your ticket with the following ticket id.\n' + \
               "Ticket Id: " + f'{support_ticket_obj.id} ' + \
               'was cancelled successfully.\n' + \
               'Please  feel free to contact us if you have any more further issues.\n' + \
               "\n\n" + \
               "\n\n" + "Thanks,\nTech-Blog Group"

    email_text = f'Subject: {subject}' \
                 f'\n' \
                 f'\n' \
                 f'{body}'

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        # print("Email sent successfully!")
        return
    except Exception as ex:
        print("Something went wrong….", ex)
        return "Error"


# def mail_for_cancelling_support_ticket(support_ticket_obj):
#     gmail_user = 'techblog.application@gmail.com'
#     gmail_password = 'techblog@123'
#     sent_from = gmail_user
#
#     subject = '[Tech-Blog] : Support Ticket '
#     # subject = 'Support Ticket'
#     user_name = User.query.filter_by(id=support_ticket_obj.u_id).first().name
#     to = User.query.filter_by(id=support_ticket_obj.u_id).first().email
#
#     if support_ticket_obj.status==True and support_ticket_obj.userdelete==False:
#         body = "Hello " + f'{user_name}, ' + "\n\n" + \
#                'Your ticket with the following ticket id.\n' + \
#                "Ticket Id: " + f'{support_ticket_obj.id} ' + \
#                'was cancelled successfully.\n' + \
#                'Please  feel free to contact us if you have any more further issues.\n' + \
#                "\n\n" + \
#                "\n\n" + "Thanks,\nTech-Blog Group"
#
#         email_text = f'Subject: {subject}' \
#                      f'\n' \
#                      f'\n' \
#                      f'{body}'
#
#         try:
#             smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#             smtp_server.ehlo()
#             smtp_server.login(gmail_user, gmail_password)
#             smtp_server.sendmail(sent_from, to, email_text)
#             smtp_server.close()
#             # print("Email sent successfully!")
#             return
#         except Exception as ex:
#             print("Something went wrong….", ex)
#     else:
#         app.logger.info("Ticket already closed")
#         return jsonify(status=404, message="Ticket already closed")


