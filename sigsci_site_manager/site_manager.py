import argparse

from api import init_api
from backup import backup
from deploy import deploy


def list_sites(args):
    print('Listing sites for "%s":' % args.corp)
    api = init_api(args.username, args.token, args.corp)
    resp = api.get_corp_sites()
    sites = [site['name'] for site in resp['data']]
    sites.sort()
    for name in sites:
        print('  %s' % name)
    print('(%d sites)' % len(sites))


def do_deploy(args):
    api = init_api(args.username, args.token, args.corp)
    deploy(api, args.site_name, args.file_name)


def clone(args):
    print('Not implemented')


def do_backup(args):
    api = init_api(args.username, args.token, args.corp)
    backup(api, args.site_name, args.file_name)


def get_args():
    # Top-level arguments
    parser = argparse.ArgumentParser(
        description='Signal Sciences site management')
    subparsers = parser.add_subparsers(title='Commands')
    parser.add_argument('--corp', '-c', metavar='CORP', required=True,
                        dest='corp', help='Signal Sciences corp name')
    parser.add_argument('--user', '-u', metavar='USERNAME', required=True,
                        dest='username', help='Signal Sciences username')
    parser.add_argument('--token', '-t', metavar='APITOKEN', required=True,
                        dest='token', help='Signal Sciences API token')

    # List command arguments
    list_parser = subparsers.add_parser('list', help='List sites')
    list_parser.set_defaults(func=list_sites)

    # Deploy command arguments
    deploy_parser = subparsers.add_parser(
        'deploy', help='Deploy a new site from a file')
    deploy_parser.add_argument('--name', '-n', metavar='NAME', required=True,
                               dest='site_name', help='Site name')
    deploy_parser.add_argument('--file', '-f', metavar='FILENAME',
                               required=True, dest='file_name',
                               help='Name of site file')
    deploy_parser.set_defaults(func=do_deploy)

    # Backup command arguments
    backup_parser = subparsers.add_parser('backup',
                                          help='Backup a site to a file')
    backup_parser.add_argument('--name', '-n', metavar='NAME', required=True,
                               dest='site_name', help='Site name')
    backup_parser.add_argument('--out', '-o', metavar='FILENAME',
                               required=True, dest='file_name',
                               help='File to save backup to')
    backup_parser.set_defaults(func=do_backup)

    # Clone command arguments
    clone_parser = subparsers.add_parser(
        'clone', help='Clone an existing site to a new site')
    clone_parser.set_defaults(func=clone)
    clone_parser.add_argument('--src', '-s', metavar='SITE', dest='src_site',
                              required=True, help='Site to clone from')
    clone_parser.add_argument('--dest', '-d', metavar='SITE', dest='dst_site',
                              required=True, help='Site to clone to')

    # Return the parsed arguments
    return parser.parse_args()


def main():
    args = get_args()
    args.func(args)


if __name__ == '__main__':
    main()
