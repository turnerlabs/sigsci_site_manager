from sigsci_site_manager.backup import backups
from sigsci_site_manager.deploy import deploys


def clone(api, src_site, dst_site, display_name, categories=None):
    print("Cloning site '%s' to new site '%s'..." % (src_site, dst_site))
    data = backups(api, src_site)
    deploys(api, dst_site, data, display_name, categories)
