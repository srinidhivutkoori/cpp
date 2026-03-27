"""
Amazon SES service for sending email notifications.
Handles submission confirmations, review assignments, and decision notifications.
"""

from datetime import datetime


class SESService:
    """
    Manages email notifications using Amazon SES in production
    and an in-memory email log in mock mode.

    Attributes:
        use_aws (bool): Whether to connect to real SES.
        sender_email (str): Default sender email address.
        client: Boto3 SES client (None in mock mode).
        sent_emails (list): Log of sent emails for mock mode.
    """

    def __init__(self, use_aws=False, sender_email='noreply@confpaper.example.com', region='eu-west-1'):
        """
        Initialize the SES service.

        Args:
            use_aws (bool): If True, connect to real AWS SES.
            sender_email (str): Sender email address.
            region (str): AWS region for SES.
        """
        self.use_aws = use_aws
        self.sender_email = sender_email
        self.region = region
        self.client = None
        self.sent_emails = []

        if self.use_aws:
            import boto3
            self.client = boto3.client('ses', region_name=region)

    def send_email(self, to_email, subject, body_text, body_html=None):
        """
        Send an email using SES or log it in mock mode.

        Args:
            to_email (str): Recipient email address.
            subject (str): Email subject line.
            body_text (str): Plain text body.
            body_html (str, optional): HTML body content.

        Returns:
            dict: Send result with message ID and status.
        """
        timestamp = datetime.utcnow().isoformat()

        if self.use_aws:
            body = {'Text': {'Data': body_text, 'Charset': 'UTF-8'}}
            if body_html:
                body['Html'] = {'Data': body_html, 'Charset': 'UTF-8'}

            response = self.client.send_email(
                Source=self.sender_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': body
                }
            )
            return {
                'message_id': response['MessageId'],
                'status': 'sent',
                'to': to_email,
                'subject': subject,
                'sent_at': timestamp
            }
        else:
            # Mock mode: log the email
            email_record = {
                'message_id': f"mock-{len(self.sent_emails) + 1:04d}",
                'from': self.sender_email,
                'to': to_email,
                'subject': subject,
                'body_text': body_text,
                'body_html': body_html,
                'status': 'sent (mock)',
                'sent_at': timestamp
            }
            self.sent_emails.append(email_record)
            return email_record

    def send_submission_confirmation(self, author_email, author_name, paper_title, conference_name):
        """
        Send a confirmation email when a paper is submitted.

        Args:
            author_email (str): Author's email.
            author_name (str): Author's full name.
            paper_title (str): Title of the submitted paper.
            conference_name (str): Name of the target conference.

        Returns:
            dict: Send result.
        """
        subject = f"Paper Submission Received - {conference_name}"
        body = (
            f"Dear {author_name},\n\n"
            f"Your paper \"{paper_title}\" has been successfully submitted to {conference_name}.\n\n"
            f"You will be notified when reviews are available.\n\n"
            f"Best regards,\nConference Management System"
        )
        return self.send_email(author_email, subject, body)

    def send_review_assignment(self, reviewer_email, reviewer_name, paper_title, deadline):
        """
        Send a notification when a reviewer is assigned to a paper.

        Args:
            reviewer_email (str): Reviewer's email.
            reviewer_name (str): Reviewer's name.
            paper_title (str): Paper title to review.
            deadline (str): Review deadline date.

        Returns:
            dict: Send result.
        """
        subject = f"Review Assignment - {paper_title}"
        body = (
            f"Dear {reviewer_name},\n\n"
            f"You have been assigned to review the paper: \"{paper_title}\".\n\n"
            f"Please complete your review by {deadline}.\n\n"
            f"Best regards,\nConference Management System"
        )
        return self.send_email(reviewer_email, subject, body)

    def send_decision_notification(self, author_email, author_name, paper_title, decision):
        """
        Send the final decision notification to an author.

        Args:
            author_email (str): Author's email.
            author_name (str): Author's name.
            paper_title (str): Paper title.
            decision (str): Decision (accepted/rejected).

        Returns:
            dict: Send result.
        """
        subject = f"Paper Decision - {paper_title}"
        body = (
            f"Dear {author_name},\n\n"
            f"We are writing to inform you that your paper \"{paper_title}\" "
            f"has been {decision}.\n\n"
            f"Best regards,\nConference Management System"
        )
        return self.send_email(author_email, subject, body)

    def get_sent_emails(self):
        """
        Retrieve log of all sent emails (mock mode only).

        Returns:
            list: List of sent email records.
        """
        return self.sent_emails

    def get_status(self):
        """
        Check SES service status.

        Returns:
            dict: Service status information.
        """
        if self.use_aws:
            try:
                self.client.get_send_quota()
                return {'service': 'SES', 'status': 'connected', 'mode': 'aws'}
            except Exception as e:
                return {'service': 'SES', 'status': 'error', 'error': str(e)}
        else:
            return {
                'service': 'SES',
                'status': 'running',
                'mode': 'mock',
                'emails_sent': len(self.sent_emails)
            }
