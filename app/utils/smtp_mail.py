import smtplib
import string
import random  # define the random module
from app.utils.form_validation import password_validator


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


def send_mail_to_reset_password(to, body):

    gmail_user = 'techblog.application@gmail.com'
    gmail_password = 'techblog@123'

    password = generate_temp_password_and_check()

    sent_from = gmail_user
    # subject = '[Tech-Blog] : Reset Password'
    subject = 'Forgot Password'
    body = "Hello " + f'{body}, ' + "\n\n\n" + \
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