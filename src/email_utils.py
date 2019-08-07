import smtplib,ssl

def send_mail(posts):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "hemant0328@gmail.com"
    receiver_email = "hemant0328@gmail.com"
    password = "vnulmsovcfajklyr"
    message = """
    Subject : Last half an our top posts\n"""
    for post in posts:
        message = message + str(post).encode("ascii","ignore").decode("ascii")
    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp_server, port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
