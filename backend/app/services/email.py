"""
Outgoing email delivery.

When ``SMTP_HOST`` is configured the message is sent over SMTP; otherwise it is
persisted in the ``email_outbox`` table (dev transport) so nothing is silently
lost and the flow stays testable.
"""
import asyncio
import smtplib
from email.message import EmailMessage

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import EmailOutbox


def _send_smtp(
    host: str,
    port: int,
    user: str,
    password: str,
    use_tls: bool,
    sender: str,
    to_email: str,
    subject: str,
    body: str,
) -> None:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(host, port, timeout=15) as smtp:
        if use_tls:
            smtp.starttls()
        if user:
            smtp.login(user, password)
        smtp.send_message(message)


async def send_email(db: AsyncSession, *, to_email: str, subject: str, body: str) -> str:
    """Send an email, returning the delivery status ('sent' | 'queued' | 'error')."""
    settings = get_settings()
    status = "queued"
    error = None

    if settings.SMTP_HOST:
        try:
            await asyncio.to_thread(
                _send_smtp,
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                settings.SMTP_USER,
                settings.SMTP_PASSWORD,
                settings.SMTP_USE_TLS,
                settings.SMTP_FROM,
                to_email,
                subject,
                body,
            )
            status = "sent"
        except Exception as exc:  # pragma: no cover - depends on the SMTP server
            status = "error"
            error = str(exc)

    db.add(
        EmailOutbox(to_email=to_email, subject=subject, body=body, status=status, error=error)
    )
    await db.commit()
    return status
