from sigsci_site_manager.consts import CATEGORIES, VALID_ROLES


def filter_data(data, keys, optional_keys=[]):
    if isinstance(data, (list, tuple)):
        ret = []
        for item in data:
            # Only save the data required by the create API
            r = {k: item[k] for k in keys}
            for k in optional_keys:
                if k in item:
                    r[k] = item[k]
            ret.append(r)
    elif data is None:
        ret = {}
    else:
        ret = {k: data[k] for k in keys}
        for k in optional_keys:
            if k in item:
                ret[k] = item[k]
    return ret


def _equal_single(a, b):
    # Single conditions have simple values
    for key in ['field', 'operator', 'value']:
        if a[key] != b[key]:
            return False
    return True


def _equal_multival(a, b):
    # groupOperator is part of both group and multival
    if a['groupOperator'] != b['groupOperator']:
        return False

    if a['type'] == 'multival':
        # multival has additional fields
        for key in ['field', 'operator']:
            if a[key] != b[key]:
                return False

    # Make sure there are the same number of conditions before doing
    # anything more complicated
    if len(a['conditions']) != len(b['conditions']):
        return False

    # Loop through all in list a
    match_all = False
    for conda in a['conditions']:
        # Compare the element in a against all in list b
        for condb in b['conditions']:
            # Check each field for a match
            match = True
            for key in ['type', 'field', 'operator', 'value']:
                if conda[key] != condb[key]:
                    # Non-matching field found
                    match = False
            if match:
                # Found a match so stop looping through b
                break
        else:
            # Nothing in b matched the item from a so stop looping
            break
    else:
        # Never broke from the loop of a due to not matches so all must
        # have matched
        match_all = True

    return match_all


def equal_conditions(a, b):
    ret = False
    if a['type'] == b['type']:
        if a['type'] == 'single':
            ret = _equal_single(a, b)
        elif a['type'] in ('group', 'multival'):
            ret = _equal_multival(a, b)
    return ret


def equal_rules(in_a, in_b, signal_rule=False):
    """
    Compares the details of a request or signal rule, exluding some fields
    that should not be compared.
    """
    if signal_rule:
        # Signal rules have an implied action
        keys = ['groupOperator', 'conditions', 'signal']
        simple_fields = ['groupOperator', 'signal']
    else:
        # Request rules have an explicit action
        keys = ['groupOperator', 'conditions', 'action', 'signal']
        simple_fields = ['groupOperator', 'action', 'signal']

    a = filter_data(in_a, keys)
    b = filter_data(in_b, keys)

    # Check the simple fields first
    for key in simple_fields:
        if a[key] != b[key]:
            return False

    # Make sure there are the same number of conditions before doing anything
    # more complicated
    if len(a['conditions']) != len(b['conditions']):
        return False

    match_all = False
    for conda in a['conditions']:
        for condb in b['conditions']:
            if equal_conditions(conda, condb):
                break
        else:
            # No condition in b matched the one from a
            break
    else:
        match_all = True

    return match_all


def build_category_list(include: list = None, exclude: list = None):
    if include and exclude:
        raise ValueError("include and exclude are mutually exclusive")
    categories = set(CATEGORIES)
    if include:
        categories = set(include)
    elif exclude:
        categories -= set(exclude)
    return categories


def add_new_user(api, email, role, api_user):
    """
        This function is to accomodate changes to sigsci api. The features
        need to be periodically reviewed incase sigsci backtracks on the
        changes.
        https://docs.signalsciences.net/whats-new/#changes-to-the-user-api
        https://docs.signalsciences.net/whats-new/#updated-permissions-and-roles
    """
    # Validate roles
    if role not in VALID_ROLES:
        raise ValueError(
            "Invalid role '{0}' passed to add_new_user".format(role))

    user = None
    # Build the user data structure
    data = {
        'role': role,
        'memberships': {
            'data': [{
                'site': {
                    'name': api.site
                }
            }]
        },
        'apiUser': api_user
    }
    add_user = False
    update_user = False
    try:
        # Generic Exception will be thrown if user does not exist
        user = api.get_corp_user(email)
        memberships = api.get_memberships(email)

        for membership in memberships['data']:
            if role != membership['role']:
                print('site:{0} changing role from {1} to {2}'.format(
                    membership['site']['name'], membership['role'], role))
            # copy the existing memberships
            if membership['site']['name'].lower() != api.site.lower():
                data['memberships']['data'].append(
                    {'site': {'name': membership['site']['name']}})
                update_user = True

        if api_user:
            # API users can't be added as API users directly so update
            # after adding to enable API
            update_user = True
    except Exception as ex:
        add_user = True
    finally:
        if add_user:
            api.add_corp_user(email, data)
    
    if update_user:
        api.update_corp_user(email, data)
