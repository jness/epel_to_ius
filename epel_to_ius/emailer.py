import smtplib
from socket import error

def email(toaddr, fromaddr, pkgs):
    '''Send email notifications'''
    subject = '[epel_to_ius] Results'
    header = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n"
                     % (fromaddr, toaddr, subject))

    body = ''
    for pkg in sorted(pkgs):
        body = body + '\n====== ' + pkg + ' ======\n'
        for p in pkgs[pkg]:
            body = body + str(p) + '\n'

    # build the email
    msg = header + body

    try:
        server = smtplib.SMTP('localhost')
        server.set_debuglevel(0)
    except error:
        raise Exception('Unable to connect to SMTP server')
    else:
        server.sendmail(fromaddr, toaddr, msg)
        server.quit()
    return
