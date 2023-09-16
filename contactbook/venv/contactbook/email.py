import smtplib, ssl

port = 587  # For starttls
smtp_server = "smtp.gmail.com"
sender_email = "contactbook.app.test@gmail.com"
password = 'vuln gsww ntec kxbv'

def send_mail(receiver, msg)->str:

    message = f"""\

    This message {msg} is sent from the contactbook app."""

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver, message)
    return f'{msg} is sent'

