import logging
import smtplib

from src.config.settings import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

logger = logging.getLogger(__name__)


def notify_task_assigned(user, task):
    subject = f'New task assigned: {task.title}'
    body = (
        f'Hello {user.name},\n\n'
        f"Task '{task.title}' has been assigned to you.\n\n"
        f'Priority: {task.priority}\nStatus: {task.status}'
    )
    _send_email(user.email, subject, body)


def notify_task_overdue(user, task):
    subject = f'Overdue task: {task.title}'
    body = (
        f'Hello {user.name},\n\n'
        f"Task '{task.title}' is overdue!\n\nDue date: {task.due_date}"
    )
    _send_email(user.email, subject, body)


def _send_email(to, subject, body):
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.info('[EMAIL STUB] To: %s | Subject: %s', to, subject)
        return

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to, f'Subject: {subject}\n\n{body}')
        server.quit()
        logger.info('Email sent to %s', to)
    except Exception as e:
        logger.error('Failed to send email: %s', str(e))
