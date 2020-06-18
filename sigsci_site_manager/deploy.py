from collections import OrderedDict
import json

from sigsci_site_manager.consts import (RULE_LISTS,
                                        CUSTOM_SIGNALS,
                                        REQUEST_RULES,
                                        SIGNAL_RULES,
                                        TEMPLATED_RULES,
                                        CUSTOM_ALERTS,
                                        SITE_MEMBERS,
                                        INTEGRATIONS,
                                        ADVANCED_RULES)
from sigsci_site_manager.util import add_new_user, filter_data


def create_site(api, site_name, data, display_name):
    # Create new site
    if not display_name:
        display_name = site_name
    print("Creating site '%s' (%s)..." % (display_name, site_name))
    data['name'] = site_name
    data['displayName'] = display_name
    try:
        api.create_corp_site(data)
    except Exception as e:  # pylint: disable=broad-except
        print('Error: %s' % e)
        return False
    return True


def create_rule_lists(api, data):
    print('Creating lists...')
    for item in data:
        print('  %s' % item['name'])
        api.add_rule_lists(item)


def create_custom_signals(api, data):
    print('Creating custom signals...')
    for item in data:
        print('  %s' % item['shortName'])
        api.add_custom_signals(item)


def create_request_rules(api, data):
    print('Creating request rules...')
    for item in data:
        print('  %s' % item['reason'])
        api.add_request_rules(item)


def create_signal_rules(api, data):
    print('Creating signal rules...')
    for item in data:
        print('  %s' % item['reason'])
        api.add_signal_rules(item)


def update_templated_rules(api, data):
    print('Updating templated rules...')
    for item in data:
        print('  %s' % item)
        api.add_templated_rules(item, data[item])


def create_custom_alerts(api, data):
    print('Creating custom alerts...')
    for item in data:
        if item['action'] == 'siteMetricInfo':
            # Default agent alerts are added at site creation
            continue
        print('  %s' % item['longName'])
        api.add_custom_alert(item)


def add_site_members(api, data):
    print('Adding users...')

    # Get existing corp users in case user needs to be added
    keys = ['email']
    src = api.get_corp_users()
    users = [user['email'] for user in filter_data(src['data'], keys)]
    for item in data:
        if item['user']['email'] not in users:
            # User does not exist in corp so invite it to the corp and add it
            # to the site
            print('  %s (New user - Corp role: %s, API user: %s)' %
                  (item['user']['email'],
                   item['role'],
                   item['user']['apiUser']))
            add_new_user(api,
                         item['user']['email'],
                         item['role'],
                         item['user']['apiUser'])
        elif item['role'] == 'owner':
            # Owners are auto-added at site creation
            continue
        else:
            # User exists in corp and is not an owner to add it to the site
            print('  %s' % item['user']['email'])
            api.add_members_to_site({"members": [item['user']['email']]})


def create_integrations(api, data):
    print('Adding integrations...')
    for item in data:
        print('  %s' % item['name'])
        try:
            api.add_integration(item)
        except Exception as e:  # pylint: disable=broad-except
            print('    Failed: %s' % e)


def create_advanced_rules(api, source, data):
    print('Creating advanced rules...')
    for item in data:
        if '+' in item['shortName']:
            print("    Warning for %s: Rule names containing '+' not supported."
                  % item['shortName'])
        try:
            response = api.copy_advanced_rule(item['shortName'],
                                              source['site']) or item
            # if response is None:
            #     response = item
            print('  %s (ID %s)' % (response['shortName'], response['id']))
        except KeyError:
            print('    Failed on %s: %s' % (item['shortName'],
                                            response['message']))
        except Exception as e:  # pylint: disable=broad-except
            print('    Failed on %s: %s' % (item['shortName'], e))




def deploys(api, site_name, data, display_name, categories):
    # Check that the site doesn't already exist
    try:
        api.get_corp_site(site_name)
    except Exception as e:  # pylint: disable=broad-except
        # If the site is not found we can continue
        if 'Site not found' in str(e):
            pass
        else:
            # Some other error happened so re-raise the exception
            raise
    else:
        # Site was successfully retrieved, which means it already exists
        print("Site '%s' already exists" % site_name)
        return

    if not create_site(api, site_name, data['site'], display_name):
        return

    api.site = site_name

    steps = OrderedDict()
    steps[RULE_LISTS] = (
        create_rule_lists, (api, data['rule_lists'])
    )
    steps[CUSTOM_SIGNALS] = (
        create_custom_signals, (api, data['custom_signals'])
    )
    steps[REQUEST_RULES] = (
        create_request_rules, (api, data['request_rules'])
    )
    steps[SIGNAL_RULES] = (
        create_signal_rules, (api, data['signal_rules'])
    )
    steps[TEMPLATED_RULES] = (
        update_templated_rules, (api, data['templated_rules'])
    )
    steps[CUSTOM_ALERTS] = (
        create_custom_alerts, (api, data['custom_alerts'])
    )
    steps[SITE_MEMBERS] = (
        add_site_members, (api, data['site_members'])
    )
    steps[INTEGRATIONS] = (
        create_integrations, (api, data['integrations'])
    )
    steps[ADVANCED_RULES] = (
        create_advanced_rules,
        (api, data['source'], data['advanced_rules'])
    )

    for k in steps:
        if categories and k in categories:
            steps[k][0](*steps[k][1])
        else:
            print('Skipping %s (excluded)' % k)


def deploy(api, site_name, file_name, display_name, categories=None):
    print("Deploying to new site '%s' from file '%s'..." %
          (site_name, file_name))

    with open(file_name, 'r') as f:
        data = json.loads(f.read())

    deploys(api, site_name, data, display_name, categories)
