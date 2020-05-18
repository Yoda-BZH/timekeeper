#!/usr/bin/env python3
#
# Get a list of EWS calendar events for a specific user
# in JSON format
#

# Imports

## Builtins
import json
import sys
import argparse

## Other
from exchangelib import DELEGATE, IMPERSONATION, Account, Credentials, \
    Configuration, NTLM, GSSAPI, Build, Version, EWSDateTime, CalendarItem, EWSTimeZone


parser = argparse.ArgumentParser()
parser.add_argument('--start',     required=True, help="Hostname of the server")
parser.add_argument('--stop',     required=True, help="File with the results")
parser.add_argument('--login', required=True, help="login")
parser.add_argument('--mail', required=True, help="User login")
parser.add_argument('--server', required=True)

args = parser.parse_args()

# Argument parsing
# TODO: use ArgParse instead
dateStart     = args.start.split('-')
dateEnd       = args.stop.split('-')
user_login    = args.login
user_mail     = args.mail
server        = args.server
user_password = input("")

# Setup exchangelib necessary objects
ews_credentials   = Credentials(user_login, user_password)
ews_configuration = Configuration(server=server, credentials=ews_credentials)

# Try to login to EWS, using user supplied parameters, and bail if an error happens
try:
    account = Account(primary_smtp_address=user_mail,
                         config=ews_configuration,
                         autodiscover=False,
                         access_type=DELEGATE
                     )
except:
    print(json.dumps({'errors': "Unable to discover exchange server"}))
    sys.exit(1)

#for item in account.inbox.all().order_by('-datetime_received')[:5]:
#    print(item.subject, item.sender, item.datetime_received)

#sys.exit(0)

start = account.default_timezone.localize(EWSDateTime(int(dateStart[0]), int(dateStart[1]), int(dateStart[2])))
end   = account.default_timezone.localize(EWSDateTime(int(dateEnd[0]), int(dateEnd[1]), int(dateEnd[2])))

def calendarItemNormalize(item):
    """
    Normalize a supplied EWS calendar event object
    """
    event = {
      'type':  'exchange',
      'uid': item.uid,
      'title': item.subject,
    }
    event.update({
        'start': item.start.isoformat(), #ews_timezone.localize(item.start),
        'end':   item.end.isoformat(), #).ews_timezone.localize(item.end),
        #'rendering': 'background',
    })

    #if item.is_all_day:
    #  event.update({ 'allDay': True })

    #if item.legacy_free_busy_status == 'OOF':
    #  event.update({'rendering': 'background'})

    return event

# Initialize items list (duh)
items = []

# Normalize every item available in user calendar and append it to
# the items list.
#for item in account.calendar.filter(start__range=(start, end)):
for item in account.calendar.view(start = start, end = end):
    #print(item.subject)
    formattedItem = calendarItemNormalize(item)
    items.append(formattedItem)
    #print(formattedItem)
    #print(json.dumps(formattedItem) + ",")

# Send items back to the user / script
print(json.dumps(items))
