from pysigsci import sigsciapi


def noop(*args, **kwargs):
    return


def init_api(username, password, token, corp, dry_run=False):
    api = sigsciapi.SigSciApi(
        email=username, password=password, api_token=token)
    api.corp = corp

    if dry_run:
        # When doing a dry run override the API methods that make changes so
        # that they do nothing. Still need the methods that get things to
        # work so that changes can be determined.
        print('Dry run...')
        api.create_corp_site = noop
        api.add_rule_lists = noop
        api.add_custom_signals = noop
        api.add_request_rules = noop
        api.add_signal_rules = noop
        api.add_templated_rules = noop
        api.add_custom_alert = noop
        api.update_rule_lists = noop
        api.update_custom_alert = noop
        api.update_site_member = noop
        api.add_integration = noop
        api.update_integration = noop

    return api
