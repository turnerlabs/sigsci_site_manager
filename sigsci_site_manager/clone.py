from backup import backups
from deploy import deploys


def clone(api, src_site, dst_site):
    data = backups(api, src_site)
    deploys(api, dst_site, data)
