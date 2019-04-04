import sigsci_site_manager.merge as merge


class DummyAPI(object):
    def __init__(self, existing, expected):
        self.existing = existing
        self.expected = expected

    def get_rule_lists(self):
        return {'data': self.existing['rule_lists']}

    def update_rule_lists(self, list_id, expected):
        assert self.expected['rule_lists'][list_id] == expected

    def add_rule_lists(self, expected):
        assert self.expected['rule_lists']['new'] == expected


def test_merge_rule_lists_no_change():
    existing = {
        'rule_lists': [{
            'id': '1',
            'name': 'existing list',
            'type': 'ip',
            'description': 'existing list',
            'entries': ['1.1.1.1']
        }]
    }
    expected = {
        'rule_lists': {
            '1': {
                'name': 'existing list',
                'type': 'ip',
                'description': 'existing list',
                'entries': ['1.1.1.1']
            }
        }
    }
    api = DummyAPI(existing, expected)

    test_data = [{
        'name': 'existing list',
        'type': 'ip',
        'description': 'existing list',
        'entries': ['1.1.1.1']
    }]
    merge.merge_rule_lists(api, test_data)


def test_merge_rule_lists_add_new():
    existing = {
        'rule_lists': [{
            'id': '1',
            'name': 'existing list',
            'type': 'ip',
            'description': 'existing list',
            'entries': ['1.1.1.1']
        }]
    }
    expected = {
        'rule_lists': {
            '1': {
                'id': '1',
                'name': 'existing list',
                'type': 'ip',
                'description': 'existing list',
                'entries': ['1.1.1.1']
            },
            'new': {
                'name': 'new list',
                'type': 'ip',
                'description': 'new list',
                'entries': ['2.2.2.2']
            }
        }
    }
    api = DummyAPI(existing, expected)

    test_data = [{
        'name': 'new list',
        'type': 'ip',
        'description': 'new list',
        'entries': ['2.2.2.2']
    }]
    merge.merge_rule_lists(api, test_data)


def test_merge_rule_lists_updated():
    existing = {
        'rule_lists': [{
            'id': '1',
            'name': 'existing list',
            'type': 'ip',
            'description': 'existing list',
            'entries': ['1.1.1.1']
        }]
    }
    expected = {
        'rule_lists': {
            '1': {
                'entries': {
                    'additions': ['2.2.2.2'],
                    'deletions': []
                }
            }
        }
    }
    api = DummyAPI(existing, expected)

    test_data = [{
        'name': 'existing list',
        'type': 'ip',
        'description': 'existing list',
        'entries': ['2.2.2.2']
    }]
    merge.merge_rule_lists(api, test_data)


def test_merge_rule_lists_add_new_different_type():
    existing = {
        'rule_lists': [{
            'id': '1',
            'name': 'existing list',
            'type': 'ip',
            'description': 'existing list',
            'entries': ['1.1.1.1']
        }]
    }
    expected = {
        'rule_lists': {
            '1': {
                'id': '1',
                'name': 'existing list',
                'type': 'ip',
                'description': 'existing list',
                'entries': ['1.1.1.1']
            },
            'new': {
                'name': 'existing list-string',
                'type': 'string',
                'description': 'existing list',
                'entries': ['foobar']
            }
        }
    }
    api = DummyAPI(existing, expected)

    test_data = [{
        'name': 'existing list',
        'type': 'string',
        'description': 'existing list',
        'entries': ['foobar']
    }]
    merge.merge_rule_lists(api, test_data)


def test_merge_rule_lists_add_new_different_type_no_change():
    existing = {
        'rule_lists': [
            {
                'id': '1',
                'name': 'existing list',
                'type': 'ip',
                'description': 'existing list',
                'entries': ['1.1.1.1']
            },
            {
                'id': '2',
                'name': 'existing list-string',
                'type': 'string',
                'description': 'existing list',
                'entries': ['foobar']
            }
        ]
    }
    expected = {
        'rule_lists': {
            '1': {
                'id': '1',
                'name': 'existing list',
                'type': 'ip',
                'description': 'existing list',
                'entries': ['1.1.1.1']
            },
            '2': {
                'name': 'existing list-string',
                'type': 'string',
                'description': 'existing list',
                'entries': ['foobar']
            }
        }
    }
    api = DummyAPI(existing, expected)

    test_data = [{
        'name': 'existing list',
        'type': 'string',
        'description': 'existing list',
        'entries': ['foobar']
    }]
    merge.merge_rule_lists(api, test_data)


def test_find_match():
    one = {'key1': 1, 'key2': 2}
    two = {'key1': 1, 'key2': 5}
    three = {'key1': 2, 'key2': 3}
    haystack = [one, two, three]
    needle = {'key1': 2, 'key2': 4, 'key3': 3}

    assert merge._find_match(needle, haystack, ['key1']) == three
    assert merge._find_match(needle, haystack, ['key2']) is None
    assert merge._find_match(needle, haystack, ['key3']) is None
