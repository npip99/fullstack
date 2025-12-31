from email.message import EmailMessage

import aiosmtplib

from src.config import credentials
from src.logger import get_logger

logger = get_logger()


async def send_signup_email(
    user_email: str,
    name: str,
) -> None:
    if credentials.email is not None:
        msg = EmailMessage()
        msg["From"] = credentials.email.email_address
        msg["To"] = user_email
        msg["Subject"] = "Welcome to FullstackTemplate!"
        if len(name) > 0:
            start = f"Hello {name}!"
        else:
            start = "Hello!"
        msg.set_content(
            f"""{start}

You have just joined the FullstackTemplate community!

Best regards,
The FullstackTemplate Team
""".strip()
        )

        # Send the email asynchronously
        try:
            await aiosmtplib.send(
                msg,
                hostname=credentials.email.hostname,
                port=credentials.email.port,
                use_tls=False,
                start_tls=True,
                username=credentials.email.email_address,
                password=credentials.email.email_password.get_secret_value(),
            )
            logger.info(f"Invite email sent to {user_email}")
        except Exception as e:
            logger.exception(f"Failed to send invite email to {user_email}: {e}")
