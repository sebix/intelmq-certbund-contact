from intelmq_certbund_contact.rulesupport import Directive


def determine_directives(context):
    context.logger.debug("============= 20_default.py ===========")

    if context.section == "destination":
        # We are not interested in notifying the contact for the
        # destination of this event.
        return

    if context.get("classification.taxonomy") not in ('abusive-content', 'fraud', 'information-content-security', 'intrusions', 'malicious-code', 'vulnerable'):
        # Skip 'availability', 'information-gathering', 'intrusion-attempts', 'other', 'test'
        context.logger.debug("Taxonomy %r not covered by this rule", context.get("classification.taxonomy"))
        return

    # Debugging output on the context
    context.logger.debug("Context Matches: %r", context.matches)

    # Generate Directives from the matches
    for match in context.matches:
        # Iterate the matches...
        # Matches tell us the organisations and their contacts that
        # could be determined for a property of the event, such as
        # IP-Address, ASN, CC.
        # It can happen that one organisation has multiple matches for
        # the same criterion (for instance IP - address),
        # this happens due to overlapping networks in the contactdb

        add_directives_to_context(context, match)

    return True

def add_directives_to_context(context, match):
    # Let's have a look at the organisations associated to this match:
    context.logger.debug('Organisations associated to this match: %r', context.organisations_for_match(match))
    for org in context.organisations_for_match(match):

        if match.field == "geolocation.cc":
            # Don't send anything to to national CSIRTs
            continue

        base_directive = Directive(notification_format='demo')

        # optionally base the format on the type or other fields
        # base_directive = Directive(notification_format=context.get("classification.type"),
        #                            notification_interval=3600)

        # You can additionally aggregate by the CIDR or AS
        # match_field_name = context.section + "." + match.field
        # if match.field == "ip":
        #     base_directive.aggregate_key["cidr"] = match.address
        # else:
        #     base_directive.aggregate_by_field(match_field_name)

        # You can also group data by incoming reports
        # base_directive.aggregate_by_field("time.observation")

        # Now create the Directives
        #
        # An organisation may have multiple contacts, so we need to
        # iterate over them. In many cases this will only loop once as
        # many organisations will have only one.
        context.logger.debug('Generating directives for contacts associated to this organisation: %r', org.contacts)
        for contact in org.contacts:
            base_directive.template_name = "demo"
            base_directive.event_data_format = "csv_attached"  # could be also taken from the directive

            # Define a new directive for a email-based notification with
            # the email address from the contact and then add the
            # details determined previously and add it to the context.
            directive = Directive.from_contact(contact)
            directive.update(base_directive)
            context.add_directive(directive)

