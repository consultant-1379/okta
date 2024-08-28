from django.core.management.base import BaseCommand
from utils import emailUtils

class Command(BaseCommand):
    help = 'Command to send an email to StackCentric informing that Okta update has been unsuccessful'


    def add_arguments(self, parser):
        parser.add_argument(
        '--build-name',
         dest='build-name',
         required=True,
         default='all'
        )

        parser.add_argument(
        '--build-url',
         dest='build-url',
         required=True,
         default='all'
        )

    def handle(self, *args, **options):
        errormsg = options['errormsg']

        contacts = ["PDLSTACKCE@pdl.internal.ericsson.com"]
        subject = 'ERROR: OKTA UPDATE UNSUCCESSFUL'

        email_message = """
Dear StackCentric,

The failure of build: '{build_name}' has caused the most recent update to Okta to be unsuccessful.

Build Url:
{build_url}

Kind regards,
Okta.
        """.format(build_name=build_name, build_url=build_url)

        emailParams = {
            'recipients' : contacts,
            'fromAddress': "okta-no-reply@ericsson.com",
            'subject' : subject,
            'message' : email_message
        }

        emailUtils.sendEmail(emailParams)


