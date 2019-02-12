from pysigsci import sigsciapi


def init_api(username, password, token, corp):
    api = sigsciapi.SigSciApi(
        email=username, password=password, api_token=token)
    api.corp = corp
    return api
