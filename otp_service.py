import random
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from passlib.context import CryptContext

from models import Otp, User
from utils import Constant

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Update these with your SMTP config
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your@email.com"
SMTP_PASSWORD = "your_password"


class OtpService:

    def generate_otp(self) -> str:
        return str(random.randint(100000, 999999))

    def send_otp(self, to: str, otp: str) -> bool:
        try:
            # Delete existing OTP for this email
            Otp.objects(email=to).delete()

            otp_entity = Otp(
                email=to,
                otp=otp,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=5)
            )
            otp_entity.save()

            msg = MIMEText(f"Your OTP for password reset is: {otp}")
            msg["Subject"] = "Password Reset OTP"
            msg["From"] = SMTP_USER
            msg["To"] = to

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

            return True
        except Exception as e:
            logger.error("Error sending OTP: %s", str(e))
            return False

    def validate_otp(self, email: str, otp: str) -> bool:
        try:
            record = Otp.objects(email=email, otp=otp).first()
            return record is not None and record.expires_at > datetime.utcnow()
        except Exception as e:
            logger.error("Error validating OTP: %s", str(e))
            return False

    def reset_password(self, email: str, new_password: str) -> bool:
        try:
            user = User.objects(email=email, is_deleted=Constant.DB_FALSE).first()
            if user:
                user.password = pwd_context.hash(new_password)
                user.save()
                return True
            return False
        except Exception as e:
            logger.error("Error resetting password: %s", str(e))
            return False


otp_service = OtpService()
