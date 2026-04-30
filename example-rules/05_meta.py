"""
Helper variables and functions for notification rules
"""
from re import compile as re_compile

CONSTITUENCY_PATTERN = re_compile("^(Zielgruppe:)(.*)$")


def get_contact_group(contact):
    for annotation in contact.annotations:
        m = CONSTITUENCY_PATTERN.match(annotation.tag)
        if m:
            return m.groups()[1]
    return None


def determine_directives(context):
    context.logger.debug("============= 05_meta.py ===========")

    ### Determine the contact group (Constituency)
    for match in context.matches:
        for org in context.organisations_for_match(match):
            for contact in org.contacts:
                contact.recipient_group = get_contact_group(contact)
                context.logger.debug("Detected contact group %r for %r.", contact.recipient_group, contact.email)
