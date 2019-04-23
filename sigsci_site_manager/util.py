from sigsci_site_manager.consts import CATEGORIES


def filter_data(data, keys):
    if isinstance(data, (list, tuple)):
        ret = []
        for item in data:
            # Only save the data required by the create API
            ret.append({k: item[k] for k in keys})
    else:
        ret = {k: data[k] for k in keys}
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
