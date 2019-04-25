import argparse
import fnmatch
from getpass import getpass
import os

from sigsci_site_manager.api import init_api
from sigsci_site_manager.backup import backup
from sigsci_site_manager.clone import clone
from sigsci_site_manager.consts import CATEGORIES
from sigsci_site_manager.deploy import deploy
from sigsci_site_manager.merge import merge
from sigsci_site_manager.util import build_category_list


def do_list(args):
    print('Listing sites for "%s"%s:' %
          (args.corp, ' matching "%s"' %
           args.filter if args.filter != '*' else ''))
    api = init_api(args.username, args.password, args.token, args.corp)
    resp = api.get_corp_sites()
    sites = []
    for site in resp['data']:
        if fnmatch.fnmatch(site['name'], args.filter):
            # Only include sites that match the filter pattern
            sites.append('%s [%s]' % (site['displayName'], site['name']))
    sites.sort()
    for name in sites:
        print('  %s' % name)
    print('(%d sites)' % len(sites))


def do_deploy(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)
    deploy(api, args.site_name, args.file_name, args.display_name,
           build_category_list(args.include, args.exclude))


def do_clone(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)
    clone(api, args.src_site, args.dst_site, args.display_name,
          build_category_list(args.include, args.exclude))


def do_backup(args):
    api = init_api(args.username, args.password, args.token, args.corp)
    backup(api, args.site_name, args.file_name)


def do_merge(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)

    # Get the current sites
    resp = api.get_corp_sites()

    # Filter the sites based on the provided destination pattern
    sites = []
    for site in resp['data']:
        if fnmatch.fnmatch(site['name'], args.dst_site):
            sites.append(site['name'])

    # If the user provided an exact match name we don't want to change the
    # existing behavior of the merge command
    exact_match = False
    if len(sites) == 1 and sites[0] == args.dst_site:
        exact_match = True

    # Get confirmation of merge action if the name wasn't an exact match
    if not exact_match:
        # If no sites matched the filter print an error and return
        if not sites:
            print("No sites match '%s'" % args.dst_site)
            return
        print('Merging %s with %d site%s:' %
              (args.src_site, len(sites), 's' if len(sites) > 1 else ''))
        for site in sites:
            print('  %s' % site)
        str_input = 'Do you want to continue [y/N]? '
        if args.yes:
            # If user specified --yes print the confirmation string with 'y' to
            # give positive feedback of the action
            print('%sy' % str_input)
        else:
            cont = input(str_input)

    # If confirmed, merge with identified sites
    if exact_match or args.yes or cont.lower() in ['y', 'yes']:
        for site in sites:
            merge(api, site, args.src_site, args.file_name,
                  build_category_list(args.include, args.exclude))


def get_args():

    def _validate_category_list(value: str):
        value_list = value.upper().split(',')
        for item in value_list:
            if item not in CATEGORIES:
                raise argparse.ArgumentTypeError(
                    '%s is not a valid category %s' % (item, CATEGORIES))
        return value_list

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
    list_parser.add_argument('--filter', metavar='PATTERN', required=False,
                             default='*',
                             help='Filter site names using a wildcard pattern')

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
    deploy_cat_group = deploy_parser.add_mutually_exclusive_group()
    deploy_cat_group.add_argument(
        '--include', required=False, metavar='CATEGORY_LIST',
        type=_validate_category_list, help=(
            'CSV list of categories to include in the merge. Options: %s' %
            ', '.join(CATEGORIES)))
    deploy_cat_group.add_argument(
        '--exclude', required=False, metavar='CATEGORY_LIST',
        type=_validate_category_list, help=(
            'CSV list of categories to include in the merge. Options: %s' %
            ', '.join(CATEGORIES)))

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
    clone_cat_group = clone_parser.add_mutually_exclusive_group()
    clone_cat_group.add_argument(
        '--include', required=False, metavar='CATEGORY_LIST',
        type=_validate_category_list, help=(
            'CSV list of categories to include in the merge. Options: %s' %
            ', '.join(CATEGORIES)))
    clone_cat_group.add_argument(
        '--exclude', required=False, metavar='CATEGORY_LIST',
        type=_validate_category_list, help=(
            'CSV list of categories to include in the merge. Options: %s' %
            ', '.join(CATEGORIES)))

    # Merge command arguments
    merge_parser = subparsers.add_parser(
        'merge', help='Merge a site onto another')
    merge_parser.set_defaults(func=do_merge)
    merge_parser.add_argument(
        '--dest', '-d', metavar='SITE', dest='dst_site', required=True,
        help='Site to merge onto (accepts wildcard pattern)')
    merge_src_group = merge_parser.add_mutually_exclusive_group()
    merge_src_group.add_argument('--src', '-s', metavar='SITE',
                                 dest='src_site', help='Site to merge from')
    merge_src_group.add_argument('--file', '-f', metavar='FILENAME',
                                 dest='file_name',
                                 help='Name of site file to merge from')
    merge_parser.add_argument('--dry-run', required=False,
                              action='store_true', dest='dry_run',
                              help='Print actions without making any changes')
    merge_cat_group = merge_parser.add_mutually_exclusive_group()
    merge_cat_group.add_argument(
        '--include', required=False, metavar='CATEGORY_LIST',
        type=_validate_category_list, help=(
            'CSV list of categories to include in the merge. Options: %s' %
            ', '.join(CATEGORIES)))
    merge_cat_group.add_argument(
        '--exclude', required=False, metavar='CATEGORY_LIST',
        type=_validate_category_list, help=(
            'CSV list of categories to include in the merge. Options: %s' %
            ', '.join(CATEGORIES)))
    merge_parser.add_argument('--yes', '-y', action='store_true',
                              help='Automatic yes to prompts')

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
