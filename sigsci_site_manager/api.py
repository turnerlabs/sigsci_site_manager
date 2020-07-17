from pysigsci import sigsciapi


def noop(*args, **kwargs):
    return


def update_corp_user(self, email, data):
    """
    Update user in corp
    PUT /corps/{corpName}/users/{userEmail}
    """
    return self._make_request(
        endpoint="{}/{}/users/{}".format(
            self.ep_corps, self.corp, email),
        json=data,
        method="PUT")


def init_api(username, password, token, corp, dry_run=False):
    api = sigsciapi.SigSciApi(
        email=username, password=password, api_token=token)
    api.corp = corp

    # Work around missing functionality in pysigsci
    setattr(sigsciapi.SigSciApi, 'update_corp_user', update_corp_user)

    if dry_run:
        # When doing a dry run override the API methods that make changes so
        # that they do nothing. Still need the methods that get things to
        # work so that changes can be determined.
        print('Dry run...')
        api.create_corp_site = noop
        api.add_rule_lists = noop
        api.add_custom_signals = noop
        api.add_request_rules = noop
        api.add_site_rules = noop
        api.add_signal_rules = noop
        api.add_templated_rules = noop
        api.add_custom_alert = noop
        api.update_rule_lists = noop
        api.update_custom_alert = noop
        api.update_site_member = noop
        api.add_integration = noop
        api.update_integration = noop
        api.add_corp_user = noop
        api.delete_corp_user = noop
        api.update_corp_user = noop
        api.get_requests = noop
        api.add_members_to_site = noop
        api.delete_site_member = noop
        api.copy_advanced_rule = noop

    return api
