# lib/email_service.py

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


class EmailConfig(BaseModel):
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: EmailStr = os.getenv("MAIL_FROM")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_TLS: bool = os.getenv("MAIL_TLS", "True").lower() == "true"
    MAIL_SSL: bool = os.getenv("MAIL_SSL", "False").lower() == "true"


class EmailService:
    def __init__(self):
        config = EmailConfig()
        self.conf = ConnectionConfig(
            MAIL_USERNAME=config.MAIL_USERNAME,
            MAIL_PASSWORD=config.MAIL_PASSWORD,
            MAIL_FROM=config.MAIL_FROM,
            MAIL_PORT=config.MAIL_PORT,
            MAIL_SERVER=config.MAIL_SERVER,
            MAIL_TLS=config.MAIL_TLS,
            MAIL_SSL=config.MAIL_SSL,
            USE_CREDENTIALS=True,
        )
        self.fastmail = FastMail(self.conf)

    async def send_email(
        self,
        recipients: List[EmailStr],
        subject: str,
        body: str,
        template_data: Dict[str, Any] = None,
    ):
        """
        Отправка email сообщения

        Args:
            recipients: список email адресов получателей
            subject: тема письма
            body: тело письма (может быть HTML)
            template_data: данные для шаблона (опционально)
        """
        message = MessageSchema(
            subject=subject, recipients=recipients, body=body, subtype="html"
        )

        await self.fastmail.send_message(message)
