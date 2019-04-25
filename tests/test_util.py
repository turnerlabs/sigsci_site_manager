import pytest

import sigsci_site_manager.consts as consts
import sigsci_site_manager.util as util


def test_equal_single():
    a = {
        "type": "single",
        "field": "ip",
        "operator": "equals",
        "value": "10.10.10.10"
    }
    b = {
        "type": "single",
        "field": "ip",
        "operator": "equals",
        "value": "8.8.8.8"
    }
    assert util._equal_single(a, a)
    assert not util._equal_single(a, b)


def test_equal_multival():
    a = {
        "type": "multival",
        "field": "postParameter",
        "operator": "exists",
        "groupOperator": "any",
        "conditions": [
            {
                "type": "single",
                "field": "name",
                "operator": "equals",
                "value": "foo"
            },
            {
                "type": "single",
                "field": "name",
                "operator": "equals",
                "value": "bar"
            }
        ]
    }
    b = {
        "type": "multival",
        "field": "postParameter",
        "operator": "exists",
        "groupOperator": "any",
        "conditions": [
            {
                "type": "single",
                "field": "name",
                "operator": "equals",
                "value": "bar"
            },
            {
                "type": "single",
                "field": "name",
                "operator": "equals",
                "value": "foo"
            }
        ]
    }
    c = {
        "type": "multival",
        "field": "postParameter",
        "operator": "exists",
        "groupOperator": "any",
        "conditions": [
            {
                "type": "single",
                "field": "name",
                "operator": "equals",
                "value": "foo"
            },
            {
                "type": "single",
                "field": "name",
                "operator": "equals",
                "value": "123"
            }
        ]
    }
    assert util._equal_multival(a, b)
    assert not util._equal_multival(a, c)


def test_equal_conditions():
    a = {
        "type": "single",
        "field": "ip",
        "operator": "equals",
        "value": "10.10.10.10"
    }
    b = {
        "type": "multival",
        "field": "postParameter",
        "operator": "exists",
        "groupOperator": "any",
        "conditions": [
            {
                "type": "single",
                "field": "name",
                "operator": "equals",
                "value": "bar"
            },
            {
                "type": "single",
                "field": "name",
                "operator": "equals",
                "value": "foo"
            }
        ]
    }
    assert util.equal_conditions(a, a)
    assert util.equal_conditions(b, b)
    assert not util.equal_conditions(a, b)


def test_build_category_list():
    cats = util.build_category_list(include=[consts.ADVANCED_RULES])
    assert cats == set([consts.ADVANCED_RULES])

    cats = util.build_category_list(exclude=[consts.ADVANCED_RULES])
    assert cats == set([
        consts.RULE_LISTS,
        consts.CUSTOM_SIGNALS,
        consts.REQUEST_RULES,
        consts.SIGNAL_RULES,
        consts.TEMPLATED_RULES,
        consts.CUSTOM_ALERTS,
        consts.SITE_MEMBERS,
        consts.INTEGRATIONS])

    cats = util.build_category_list()
    assert cats == set(consts.CATEGORIES)

    with pytest.raises(ValueError):
        cats = util.build_category_list(include=[consts.ADVANCED_RULES],
                                        exclude=[consts.CUSTOM_ALERTS])
