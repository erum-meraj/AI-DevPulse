import smtplib
from email.mime.text import MIMEText

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.daily_brief import DailyBrief

logger = get_logger(__name__)


class NotificationService:
    """Sends the daily brief via email over Gmail SMTP. Requires
    EMAIL_ADDRESS, EMAIL_APP_PASSWORD (a Gmail App Password, not the
    account password), and EMAIL_TO to be set in Settings. Silently skips
    sending (logs a warning) if any of these are missing, rather than
    raising -- email is a notification, not a pipeline-critical step."""

    def __init__(self):
        self.settings = get_settings()

    def send_daily_brief_email(self, brief: DailyBrief) -> bool:
        if not (
            self.settings.EMAIL_ADDRESS
            and self.settings.EMAIL_APP_PASSWORD
            and self.settings.EMAIL_TO
        ):
            logger.warning("daily_brief_email_skipped", reason="email settings not configured")
            return False

        body = self._format_email_body(brief)
        message = MIMEText(body, "plain")
        message["Subject"] = f"AI DevPulse — Daily Brief for {brief.date.isoformat()}"
        message["From"] = self.settings.EMAIL_ADDRESS
        message["To"] = self.settings.EMAIL_TO

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.settings.EMAIL_ADDRESS, self.settings.EMAIL_APP_PASSWORD)
                server.send_message(message)
            logger.info("daily_brief_email_sent", date=str(brief.date))
            return True
        except Exception as exc:
            logger.error("daily_brief_email_failed", date=str(brief.date), error=str(exc))
            return False

    def _format_email_body(self, brief: DailyBrief) -> str:
        return (
            f"Good morning. You missed {brief.stories_analyzed} stories.\n\n"
            f"We've filtered them to the {brief.stories_selected} developments "
            f"that actually matter.\n\n"
            f"{brief.summary or ''}\n\n"
            f"Estimated read time: {brief.estimated_read_time_minutes} min\n"
        )
