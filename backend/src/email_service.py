from flask import current_app
from flask_mail import Message

from backend.extensions import mail


def send_password_reset_email(user):
    """
    Sends a password reset email to the user using Flask-Mail.
    """
    token = user.get_reset_token()
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password/{token}"

    subject = "Reset Your Password"
    sender = current_app.config.get("MAIL_DEFAULT_SENDER")
    recipients = [user.email]

    # You can create more elaborate HTML templates for your emails
    html_body = f"""
    <p>Hello {user.name or 'there'},</p>
    <p>You are receiving this email because you (or someone else) requested a password reset for your account.</p>
    <p>Please click the link below to reset your password:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>This link will expire in 30 minutes.</p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <p>Thanks,</p>
    <p>The Team</p>
    """

    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.html = html_body

    try:
        if not current_app.config.get("TESTING", False):
            mail.send(msg)
        else:
            # In testing, we don't want to send real emails
            print("--- SUPPRESSED PASSWORD RESET EMAIL (TESTING) ----")
            print(f"To: {user.email}")
            print(f"URL: {reset_url}")
            print("--------------------------------------------------")

    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        # Depending on your needs, you might want to handle this error more gracefully
        raise
