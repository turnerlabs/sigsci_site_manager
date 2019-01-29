import json


def create_site(api, site_name, data):
    # Create new site
    # Not currently supported by pysigsci
    # POST /corps/{corpName}/sites
    print('Creating site...')
    data['name'] = site_name
    data['displayName'] = site_name
    resp = api._make_request(
        endpoint="{}/{}/sites".format(api.ep_corps, api.corp),
        json=data,
        method="POST_JSON"
    )
    if 'message' in resp:
        print('Error: %s' % resp['message'])
        return False


def create_rule_lists(api, data):
    print('Creating lists...')
    for item in data:
        print('  %s' % item['name'])
        api.add_rule_lists(item)


def create_request_rules(api, data):
    print('Creating request rules...')
    for item in data:
        print('  %s' % item['reason'])
        api.add_request_rules(item)


def create_custom_signals(api, data):
    print('Creating custom signals...')
    import pdb
    pdb.set_trace()
    for item in data:
        print('  %s' % item['shortName'])
        api.add_custom_signals(item)


def create_custom_alerts(api, data):
    print('Creating custom alerts...')
    for item in data:
        if item['action'] is 'siteMetricInfo':
            # Default agent alerts are added at site creation
            continue
        print('  %s' % item['longName'])
        api.add_custom_alert(item)


def add_site_members(api, data):
    print('Adding users...')
    for item in data:
        if item['user']['role'] is 'owner':
            # Owners are auto-added at site creation
            continue
        print('  %s' % item['user']['email'])
        role = {'role': item['role']}
        api.update_site_member(item['user']['email'], role)


def deploy(api, site_name, file_name):
    with open(file_name, 'r') as f:
        data = json.loads(f.read())

    # Check that the site doesn't already exist
    try:
        api.get_corp_site(site_name)
    except Exception as e:
        # If the site is not found we can continue
        if 'Site not found' in str(e):
            pass
        else:
            # Some other error happened so re-raise the exception
            raise
    else:
        # Site was successfully retrieved, which means it already exists
        print("Site '%s' already exists" % site_name)
        # return

    if not create_site(api, site_name, data['site']):
        return

    api.site = site_name

    create_rule_lists(api, data['rule_lists'])
    create_custom_signals(api, data['custom_signals'])
    create_request_rules(api, data['request_rules'])
    create_custom_alerts(api, data['custom_alerts'])
    add_site_members(api, data['site_members'])
