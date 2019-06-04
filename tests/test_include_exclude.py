import pytest

import sigsci_site_manager.merge as merge
import sigsci_site_manager.deploy as deploy
import sigsci_site_manager.consts as consts


class DummyAPI(object):
    def __init__(self):
        self.site = 'dummy'
        self.corp = 'dummy'

    def get_corp_site(self, site_name):
        if site_name != 'dummy':
            raise Exception('Site not found')

    def create_corp_site(self, *args, **kwargs):
        return

    def get_corp_users(self, *args, **kwargs):
        return {'data': [{'email': 'test@test.com', 'apiUser': False}]}

    def add_corp_user(self, *args, **kwargs):
        return


API = DummyAPI()

DATA = {
    'rule_lists': [],
    'custom_signals': [{'shortName': 'dummy_signal'}],
    'request_rules': [],
    'signal_rules': [],
    'templated_rules': [],
    'custom_alerts': [],
    'site_members': [{
        'user': {'email': 'test@test.com', 'apiUser': False},
        'role': ''
    }],
    'integrations': [],
    'source': {'corp': 'dummy', 'site': 'dummy_src'},
    'advanced_rules': [],
    'site': {'name': 'dummy'}
}


def test_merge_category_include():
    # With ADVANCED_RULES included the only step is merging the advanced rules.
    # Since DummyAPI does not have a get_advanced_rules method this should
    # be the exception raised rather than one about there being no
    # get_rule_lists()
    categories = [consts.ADVANCED_RULES]
    with pytest.raises(AttributeError,
                       match="object has no attribute 'get_advanced_rules'"):
        merge.merges(API, 'dummy', DATA, categories)


def test_deploy_category_include():
    # With SITE_MEMBERS included the only step is merging the integrations.
    # Since DummyAPI does not have a update_site_member method this should
    # be the exception raised rather than one about there being no
    # get_rule_lists()
    categories = [consts.SITE_MEMBERS]
    with pytest.raises(AttributeError,
                       match="object has no attribute 'update_site_member'"):
        deploy.deploys(API, 'dummy1', DATA, 'dummy', categories)


def test_merge_category_exclude():
    categories = consts.CATEGORIES.copy()
    categories.remove(consts.RULE_LISTS)

    # With RULE_LISTS excluded the next step is merging the custom signals.
    # Since DummyAPI does not have a get_custom_signals() method this should
    # be the exception raised rather than one about there being no
    # get_rule_lists()
    with pytest.raises(AttributeError,
                       match="object has no attribute 'get_custom_signals'"):
        merge.merges(API, 'dummy', DATA, categories)


def test_deploy_category_exclude():
    categories = consts.CATEGORIES.copy()
    categories.remove(consts.RULE_LISTS)

    # With RULE_LISTS excluded the next step is deploying the custom signals.
    # Since DummyAPI does not have an add_custom_signals() method this should
    # be the exception raised rather than one about there being no
    # add_rule_lists()
    with pytest.raises(AttributeError,
                       match="object has no attribute 'add_custom_signals'"):
        deploy.deploys(API, 'dummy1', DATA, 'dummy', categories)
