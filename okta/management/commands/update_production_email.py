from django.core.management.base import BaseCommand
from utils import emailUtils

class Command(BaseCommand):
    help = 'Command to send an email to StackCentric informing that Okta will be temporarily taken down and updated'


    def handle(self, *args, **options):

        contacts = ["PDLSTACKCE@pdl.internal.ericsson.com"]
        subject = 'Okta to be temporarily taken down for update'

        email_message = """
Dear StackCentric,

Please note Okta will be temporarily taken down for an update in approximately 15 minutes.

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