import asyncio
import logging
import smtplib
from email.message import EmailMessage

_LOGGER = logging.getLogger(__name__)


async def send_forecast_email(
    smtp_host,
    smtp_port,
    smtp_user,
    smtp_pass,
    to_email,
    forecast_text,
    subject="NWS Forecast Update",
):
    _LOGGER.debug(
        "Preparing to send forecast email - SMTP: %s:%s, From: %s, To: %s, Subject: %s",
        smtp_host,
        smtp_port,
        smtp_user,
        to_email,
        subject,
    )
    _LOGGER.debug("Forecast text length: %d characters", len(forecast_text))

    try:
        # Run the synchronous SMTP operation in a thread pool
        result = await asyncio.to_thread(
            _send_email_sync,
            smtp_host,
            smtp_port,
            smtp_user,
            smtp_pass,
            to_email,
            forecast_text,
            subject,
        )

        if result:
            _LOGGER.info("Forecast sent to %s", to_email)
        return result

    except Exception as e:
        _LOGGER.exception("Failed to send forecast email: %s", str(e))
        _LOGGER.debug(
            "Email sending failed - SMTP: %s:%s, From: %s, To: %s",
            smtp_host,
            smtp_port,
            smtp_user,
            to_email,
        )
        return False


def _send_email_sync(
    smtp_host, smtp_port, smtp_user, smtp_pass, to_email, forecast_text, subject
):
    """Synchronous SMTP email sending function to be run in thread pool."""
    try:
        msg = EmailMessage()
        msg.set_content(forecast_text)
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to_email
        _LOGGER.debug("Email message prepared")

        _LOGGER.debug("Connecting to SMTP server")
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            _LOGGER.debug("SMTP connection established")

            _LOGGER.debug("Starting TLS encryption")
            server.starttls()
            _LOGGER.debug("TLS encryption enabled")

            _LOGGER.debug("Logging into SMTP server")
            server.login(smtp_user, smtp_pass)
            _LOGGER.debug("SMTP login successful")

            _LOGGER.debug("Sending email message")
            server.send_message(msg)
            _LOGGER.debug("Email message sent successfully")

        return True

    except Exception as e:
        _LOGGER.exception("Failed to send forecast email: %s", str(e))
        return False
