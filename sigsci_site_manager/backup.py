import json

from sigsci_site_manager.util import filter_data


def get_site(api):
    keys = ['agentLevel', 'blockDurationSeconds', 'blockHTTPCode']
    data = api.get_corp_site(api.site)
    return filter_data(data, keys)


def get_rule_lists(api):
    keys = ['name', 'type', 'description', 'entries']
    data = api.get_rule_lists()
    return filter_data(data['data'], keys)


def get_request_rules(api):
    keys = ['enabled', 'groupOperator', 'conditions',
            'action', 'signal', 'reason', 'expiration']
    data = api.get_request_rules()
    return filter_data(data['data'], keys)


def get_custom_signals(api):
    keys = ['tagName', 'shortName', 'description']
    data = api.get_custom_signals()
    return filter_data(data['data'], keys)


def get_signal_rules(api):
    keys = ['enabled', 'signal', 'groupOperator', 'conditions', 'reason']
    data = api.get_signal_rules()
    return filter_data(data['data'], keys)


def get_templated_rules(api):
    detection_keys = ['name', 'fields', 'enabled']
    alert_keys = ['longName', 'interval', 'threshold',
                  'skipNotifications', 'enabled', 'action']
    data = api.get_templated_rules()
    ret = {}
    for rule in data['data']:
        if not rule['detections']:
            # Skip empty rules
            continue

        # Reformat the retrieved data into the structure needed for adding the
        # templated rule to a clean site.
        ret[rule['name']] = {'detectionAdds': [], 'alertAdds': []}
        ret[rule['name']]['detectionAdds'] += filter_data(
            rule['detections'], detection_keys)
        ret[rule['name']]['alertAdds'] += filter_data(
            rule['alerts'], alert_keys)
    return ret


def get_custom_alerts(api):
    keys = ['tagName', 'longName', 'interval',
            'threshold', 'enabled', 'action']
    data = api.get_custom_alerts()
    return filter_data(data['data'], keys)


def get_site_members(api):
    keys = ['user', 'role']
    data = api.get_site_members()
    return filter_data(data['data'], keys)


def get_advanced_rules(api):
    keys = ['id', 'shortName']
    data = api.get_advanced_rules()
    return filter_data(data.get('data', []), keys)


def get_integrations(api):
    keys = ['name', 'type', 'url', 'events']
    data = api.get_integrations()
    return filter_data(data['data'], keys)


def backups(api, site_name):
    api.site = site_name

    data = {}
    data['source'] = {'corp': api.corp, 'site': api.site}
    data['site'] = get_site(api)
    data['rule_lists'] = get_rule_lists(api)
    data['request_rules'] = get_request_rules(api)
    data['custom_signals'] = get_custom_signals(api)
    data['signal_rules'] = get_signal_rules(api)
    data['templated_rules'] = get_templated_rules(api)
    data['custom_alerts'] = get_custom_alerts(api)
    data['site_members'] = get_site_members(api)
    data['advanced_rules'] = get_advanced_rules(api)
    data['integrations'] = get_integrations(api)

    return data


def backup(api, site_name, file_name):
    print("Backing up site '%s' to file '%s'..." %
          (site_name, file_name))

    data = backups(api, site_name)

    with open(file_name, 'w') as f:
        f.write(json.dumps(data))
