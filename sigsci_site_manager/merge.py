import json

from sigsci_site_manager.backup import backups
from sigsci_site_manager.util import filter_data, equal_rules


def merge_rule_lists(api, data):
    print('Merging lists...')

    # Get the existing lists
    keys = ['id', 'name', 'type', 'entries']
    src = api.get_rule_lists()
    lists = filter_data(src['data'], keys)

    # Loop through the lists to merge in
    for item in data:
        for existing in lists:
            # If there is a list of the same name try to merge it
            if existing['name'] == item['name']:
                if existing['type'] == item['type']:
                    # Lists have same type so add in missing entries
                    merged = {
                        'entries': {
                            'additions': [],
                            'deletions': []
                        }
                    }
                    for entry in item['entries']:
                        if entry not in existing['entries']:
                            # Entry exists in src but not dst
                            merged['entries']['additions'].append(entry)
                    if not merged['entries']['additions']:
                        print('  Skipping %s (no differences)' % item['name'])
                    else:
                        print('  Updating %s' % item['name'])
                        try:
                            api.update_rule_lists(existing['id'], merged)
                        except Exception as e:
                            print('    Failed: %s' % e)
                else:
                    # Lists don't have same type so create a new list. Set the
                    # name to be the original name with the new type appended.
                    # Names can only be 32 characters so need to leave space
                    # for the type.
                    item['name'] = '%s-%s' % (
                        item['name'][0:31-len(item['type'])], item['type'])

                    # Make sure this new name doesn't already exist. If it does
                    # that means it was already created on a previous merge and
                    # so will be covered on another iteration through the
                    # existing lists.
                    for existing in lists:
                        if existing['name'] == item['name']:
                            break
                    else:
                        print('  Adding %s' % item['name'])
                        try:
                            api.add_rule_lists(item)
                        except Exception as e:
                            print('    Failed: %s' % e)
                break
        else:
            # List iteration ended without breaking on a name match so add
            # the list as a new one
            print('  Adding %s' % item['name'])
            try:
                api.add_rule_lists(item)
            except Exception as e:
                print('    Failed: %s' % e)


def merge_custom_signals(api, data):
    print('Merging custom signals...')

    # Get the existing custom signals
    keys = ['tagName']
    src = api.get_custom_signals()
    lists = filter_data(src['data'], keys)

    for item in data:
        for existing in lists:
            if existing['tagName'] == item['tagName']:
                print('  Skipping %s (exists)' % item['shortName'])
                break
        else:
            # List iteration ended without breaking on a tag match so add
            # the signal as a new one
            print('  Adding %s' % item['shortName'])
            api.add_custom_signals(item)


def merge_request_rules(api, data):
    print('Merging request rules...')

    # Get the existing request rules
    keys = ['enabled', 'groupOperator', 'conditions',
            'action', 'signal', 'reason', 'expiration']
    src = api.get_request_rules()
    rules = filter_data(src['data'], keys)

    for item in data:
        for rule in rules:
            if equal_rules(rule, item):
                print('  Skipping %s (exists)' % item['reason'])
                break
        else:
            print('  Adding %s' % item['reason'])
            try:
                api.add_request_rules(item)
            except Exception as e:
                print('    Failed: %s' % e)


def merge_signal_rules(api, data):
    print('Merging signal rules...')

    # Get the existing signal rules
    keys = ['enabled', 'groupOperator', 'conditions', 'signal', 'reason', ]
    src = api.get_signal_rules()
    rules = filter_data(src['data'], keys)

    for item in data:
        for rule in rules:
            if equal_rules(rule, item, signal_rule=True):
                print('  Skipping %s (exists)' % item['reason'])
                break
        else:
            print('  Adding %s' % item['reason'])
            try:
                api.add_signal_rules(item)
            except Exception as e:
                print('    Failed: %s' % e)


def merge_templated_rules(api, data):
    print('Mergiong templated rules...')

    # Get existing templated rules. We also only care about the names of
    # configured rules because we're going to skip any configured templated
    # rules.
    src = api.get_templated_rules()
    rule_names = []
    for rule in src['data']:
        if rule['detections'] or rule['alerts']:
            rule_names.append(rule['name'])

    # Loop through the templated rules
    for item in data:
        if item in rule_names:
            # Rule name in the list of already configured rules so skip
            print('  Skipping %s (configured)' % item)
        else:
            print('  Adding %s' % item)
            try:
                pass
                api.add_templated_rules(item, data[item])
            except Exception as e:
                print('    Failed: %s' % e)


def merge_custom_alerts(api, data):
    print('Merging custom alerts...')

    # Get existing alerts
    keys = ['id', 'tagName', 'longName', 'interval',
            'threshold', 'enabled', 'action']
    src = api.get_custom_alerts()
    alerts = filter_data(src['data'], keys)

    for item in data:
        if item['action'] == 'siteMetricInfo':
            # Default agent alerts are added at site creation
            continue
        for alert in alerts:
            if (item['tagName'] == alert['tagName'] and
                    item['longName'] == alert['longName']):
                if (not alert['enabled'] and
                    (item['interval'] != alert['interval'] or
                     item['threshold'] != alert['threshold'] or
                     item['enabled'] != alert['enabled'] or
                     item['action'] != alert['action'])):
                    # Alert with same tag and description exists but is not
                    # enabled so update to match the source alert.
                    print('  Updating %s' % item['longName'])
                    api.update_custom_alert(alert['id'], item)
                    break
                else:
                    # Alert with same tag and description exists and is enabled
                    # or has the same values as the source alert so don't touch
                    # it.
                    print('  Skipping %s (exists)' % item['longName'])
                    break
        else:
            print('  Adding %s' % item['longName'])
            api.add_custom_alert(item)


def merge_site_members(api, data):
    print('Merging users...')

    # Get existing users
    keys = ['user']
    src = api.get_site_members()
    users = filter_data(src['data'], keys)

    # Loop through the users to add
    for item in data:
        for user in users:
            # Skip users that exist in the site
            if item['user']['email'] == user['user']['email']:
                print('  Skipping %s (exists)' % item['user']['email'])
                break
        else:
            # Add missing user
            print('  Adding %s' % item['user']['email'])
            role = {'role': item['role']}
            api.update_site_member(item['user']['email'], role)


def generate_advanced_rules_request(api, source, data):
    # Get the existing advanced rules
    src = api.get_advanced_rules()
    rules = filter_data(src['data'], ['shortName'])
    rule_names = [r['shortName'] for r in rules]

    email = '\n\nEmail support@signalsciences.com with the following...\n'
    email += ('Please copy the following advanced rules from %s/%s to %s/%s:' %
              (source['corp'], source['site'], api.corp, api.site))
    make_request = False
    for item in data:
        if item['shortName'] not in rule_names:
            email += '\n    %s (ID %s)' % (item['shortName'], item['id'])
            make_request = True
    if make_request:
        print(email)


def merges(api, site_name, data):
    # Check that the site already exists
    try:
        api.get_corp_site(site_name)
    except Exception as e:
        # If the site is not found we can continue
        if 'Site not found' in str(e):
            print("Site '%s' does not exist" % site_name)
            return
        else:
            # Some other error happened so re-raise the exception
            raise

    api.site = site_name

    merge_rule_lists(api, data['rule_lists'])
    merge_custom_signals(api, data['custom_signals'])
    merge_request_rules(api, data['request_rules'])
    merge_signal_rules(api, data['signal_rules'])
    merge_templated_rules(api, data['templated_rules'])
    merge_custom_alerts(api, data['custom_alerts'])
    merge_site_members(api, data['site_members'])

    generate_advanced_rules_request(
        api, data['source'], data['advanced_rules'])


def merge(api, dst_site, src_site=None, file_name=None):
    if src_site:
        print("Merging site '%s' onto site '%s'..." % (src_site, dst_site))
        data = backups(api, src_site)
    elif file_name:
        print("Merging file '%s' onto site '%s'..." % (file_name, dst_site))
        with open(file_name, 'r') as f:
            data = json.loads(f.read())

    merges(api, dst_site, data)
