from __future__ import annotations

import asyncio
from email.message import EmailMessage
from pathlib import Path
from uuid import uuid4
from typing import Any, Dict, Optional

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER, SENDER_EMAIL
from utils.logger import logger

TEMPLATES_DIR = Path(__file__).resolve().parent / "email_templates"
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


async def send_email(
    subject: str,
    recipient: str,
    text_body: str,
    html_template: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    msg["Subject"] = subject
    msg["X-Entity-Ref-ID"] = str(uuid4())  # pomaga uniknąć grupowania/zwijania w niektórych klientach

    msg.set_content(text_body)

    if html_template:
        template = jinja_env.get_template(html_template)
        html_body = template.render(**(context or {}))
        msg.add_alternative(html_body, subtype="html")

    smtp = aiosmtplib.SMTP(hostname=SMTP_HOST, port=SMTP_PORT, start_tls=True)

    try:
        await smtp.connect()
        if SMTP_USER and SMTP_PASSWORD:
            await smtp.login(SMTP_USER, SMTP_PASSWORD)
        await smtp.send_message(msg)
        await smtp.quit()
    except Exception as exc:  # pragma: no cover - network path
        logger.exception("Błąd wysyłki emaila: %s", exc)
        raise


async def send_reset_email_code(recipient_email: str, reset_code: str) -> None:
    await send_email(
        subject="Skill2Win | Reset hasła",
        recipient=recipient_email,
        text_body=f"""
Hej!

Otrzymaliśmy prośbę o reset hasła do Skill2Win. Twój jednorazowy kod to:

    {reset_code}

Kod wygasa za 15 minut. Wpisz go w aplikacji, aby dokończyć reset.

Jeśli to nie Ty inicjowałeś reset, zignoruj tę wiadomość.

Do zobaczenia w grze,
Zespół Skill2Win
""",
        html_template="reset_code.html",
        context={"reset_code": reset_code},
    )


def send_reset_email_code_sync(recipient_email: str, reset_code: str) -> None:
    """
    Synchronous helper for endpoints that are synchronous (FastAPI sync deps).
    """
    try:
        # In worker threads there is usually no running loop.
        asyncio.run(send_reset_email_code(recipient_email, reset_code))
    except RuntimeError:
        # Fallback when called from a thread that already has a loop.
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(send_reset_email_code(recipient_email, reset_code))
        finally:
            loop.close()


async def send_verification_email_code(recipient_email: str, verification_code: str) -> None:
    await send_email(
        subject="Skill2Win | Potwierdź rejestrację",
        recipient=recipient_email,
        text_body=f"""
Hej!

Witaj w Skill2Win. Twój kod potwierdzający rejestrację to:

    {verification_code}

Kod wygasa za 15 minut. Wpisz go w aplikacji, aby aktywować konto.

Jeśli to nie Ty inicjowałeś rejestrację, zignoruj tę wiadomość.

Do zobaczenia w grze,
Zespół Skill2Win
""",
        html_template="verification_code.html",
        context={"verification_code": verification_code},
    )


def send_verification_email_code_sync(recipient_email: str, verification_code: str) -> None:
    try:
        asyncio.run(send_verification_email_code(recipient_email, verification_code))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(send_verification_email_code(recipient_email, verification_code))
        finally:
            loop.close()
