import argparse
from getpass import getpass
import os

from sigsci_site_manager.api import init_api
from sigsci_site_manager.backup import backup
from sigsci_site_manager.clone import clone
from sigsci_site_manager.deploy import deploy
from sigsci_site_manager.merge import merge


def do_list(args):
    print('Listing sites for "%s":' % args.corp)
    api = init_api(args.username, args.password, args.token, args.corp)
    resp = api.get_corp_sites()
    sites = ['%s [%s]' % (site['displayName'], site['name'])
             for site in resp['data']]
    sites.sort()
    for name in sites:
        print('  %s' % name)
    print('(%d sites)' % len(sites))


def do_deploy(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)
    deploy(api, args.site_name, args.file_name, args.display_name)


def do_clone(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)
    clone(api, args.src_site, args.dst_site, args.display_name)


def do_backup(args):
    api = init_api(args.username, args.password, args.token, args.corp)
    backup(api, args.site_name, args.file_name)


def do_merge(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)
    merge(api, args.dst_site, args.src_site, args.file_name)


def get_args():
    # Top-level arguments
    parser = argparse.ArgumentParser(
        description='Signal Sciences site management')
    subparsers = parser.add_subparsers(title='Commands', dest='command')
    subparsers.required = True
    parser.add_argument('--corp', '-c', metavar='CORP', dest='corp',
                        help='Signal Sciences corp name. If omitted will try '
                             'to use value in $SIGSCI_CORP.')
    parser.add_argument('--user', '-u', metavar='USERNAME', nargs='?',
                        dest='username', const='',
                        help='Signal Sciences username. If omitted will try '
                             'to use value in $SIGSCI_EMAIL.')
    pw_group = parser.add_mutually_exclusive_group()
    pw_group.add_argument('--password', '-p', metavar='PASSWORD', nargs='?',
                          dest='password', const='',
                          help='Signal Sciences password. If omitted will try '
                               'to use value in $SIGSCI_PASSWORD')
    pw_group.add_argument('--token', '-t', metavar='APITOKEN', nargs='?',
                          dest='token', const='',
                          help='Signal Sciences API token. If omitted will '
                               'try to use value in $SIGSCI_API_TOKEN')

    # List command arguments
    list_parser = subparsers.add_parser('list', help='List sites')
    list_parser.set_defaults(func=do_list)

    # Deploy command arguments
    deploy_parser = subparsers.add_parser(
        'deploy', help='Deploy a new site from a file')
    deploy_parser.set_defaults(func=do_deploy)
    deploy_parser.add_argument('--name', '-n', metavar='NAME', required=True,
                               dest='site_name',
                               help='Identifying name of the site')
    deploy_parser.add_argument('--display-name', '-N',
                               metavar='"Display Name"', dest='display_name',
                               help='Display name of the site')
    deploy_parser.add_argument('--file', '-f', metavar='FILENAME',
                               required=True, dest='file_name',
                               help='Name of site file')
    deploy_parser.add_argument('--dry-run', required=False,
                               action='store_true', dest='dry_run',
                               help='Print actions without making any changes')

    # Backup command arguments
    backup_parser = subparsers.add_parser('backup',
                                          help='Backup a site to a file')
    backup_parser.set_defaults(func=do_backup)
    backup_parser.add_argument('--name', '-n', metavar='NAME', required=True,
                               dest='site_name', help='Site name')
    backup_parser.add_argument('--out', '-o', metavar='FILENAME',
                               required=True, dest='file_name',
                               help='File to save backup to')

    # Clone command arguments
    clone_parser = subparsers.add_parser(
        'clone', help='Clone an existing site to a new site')
    clone_parser.set_defaults(func=do_clone)
    clone_parser.add_argument('--src', '-s', metavar='SITE', dest='src_site',
                              required=True, help='Site to clone from')
    clone_parser.add_argument('--dest', '-d', metavar='SITE', dest='dst_site',
                              required=True, help='Site to clone to')
    clone_parser.add_argument('--display-name', '-N',
                              metavar='"Display Name"', dest='display_name',
                              help='Display name of the new site')
    clone_parser.add_argument('--dry-run', required=False,
                              action='store_true', dest='dry_run',
                              help='Print actions without making any changes')

    # Merge command arguments
    merge_parser = subparsers.add_parser(
        'merge', help='Merge a site onto another')
    merge_parser.set_defaults(func=do_merge)
    merge_parser.add_argument('--dest', '-d', metavar='SITE', dest='dst_site',
                              required=True, help='Site to merge onto')
    merge_src_group = merge_parser.add_mutually_exclusive_group()
    merge_src_group.add_argument('--src', '-s', metavar='SITE',
                                 dest='src_site', help='Site to merge from')
    merge_src_group.add_argument('--file', '-f', metavar='FILENAME',
                                 dest='file_name',
                                 help='Name of site file to merge from')
    merge_parser.add_argument('--dry-run', required=False,
                              action='store_true', dest='dry_run',
                              help='Print actions without making any changes')

    # Return the parsed arguments
    return parser.parse_args()


def main():
    args = get_args()

    # Username arg was passed but without a value so get it from stdin
    if args.username == '':
        args.username = getpass('Username: ')

    # Password/Token args were passed but without values
    # so get those values from stdin
    if args.password == '':
        args.password = getpass()
        args.token = None
    elif args.token == '':
        args.token = getpass('API Token: ')
        args.password = None

    # If username/password|token/corp were not specified via args see if
    # there are environment variables set
    if args.username is None and 'SIGSCI_EMAIL' in os.environ:
        args.username = os.environ['SIGSCI_EMAIL']
    if args.password is None and 'SIGSCI_PASSWORD' in os.environ:
        args.password = os.environ['SIGSCI_PASSWORD']
    if args.token is None and 'SIGSCI_API_TOKEN' in os.environ:
        args.token = os.environ['SIGSCI_API_TOKEN']
    if args.corp is None and 'SIGSCI_CORP' in os.environ:
        args.corp = os.environ['SIGSCI_CORP']

    # Validate corp/username/password|token are present
    if args.corp is None:
        print('error: corp name is required')
        return 1
    if args.username is None:
        print('error: username is required')
        return 1
    if args.password is None and args.token is None:
        print('error: password or API token is required')
        return 1

    args.func(args)
    return 0
