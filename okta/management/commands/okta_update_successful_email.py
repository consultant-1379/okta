from django.core.management.base import BaseCommand
from utils import emailUtils

class Command(BaseCommand):
    help = 'Command to send an email to StackCentric informing that Okta update has been successful'


    def handle(self, *args, **options):

        contacts = ["PDLSTACKCE@pdl.internal.ericsson.com"]
        subject = 'Okta update was successful'

        email_message = """
Dear StackCentric,

Okta has been successfully updated and is back online.

Kind regards,
Okta.
        """

        emailParams = {
            'recipients' : contacts,
            'fromAddress': "okta-no-reply@ericsson.com",
            'subject' : subject,
            'message' : email_message
        }

        emailUtils.sendEmail(emailParams)


