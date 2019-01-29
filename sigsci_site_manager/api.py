from pysigsci import sigsciapi


def init_api(username, token, corp):
    api = sigsciapi.SigSciApi(email=username, api_token=token)
    api.corp = corp
    return api
