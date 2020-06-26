import sys

from sigsci_site_manager.api import init_api
from sigsci_site_manager.util import add_new_user


def do_list_users(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)
    if args.site_name:
        api.site = args.site_name
        users = api.get_site_members()
    else:
        users = api.get_corp_users()

    cols = ['email', 'role', 'status', 'name']
    colFormat = "%45s %10s %10s %30s"
    if users:
        line_entries = []
        if args.site_name:
            print('Site: %s' % args.site_name)
            print(colFormat % (cols[0], 'site' + cols[1],
                               cols[2], cols[3]))
            for user in users['data']:
                line_entries.append(colFormat % (user['user'][cols[0]], user[cols[1]],
                                                 user['user'][cols[2]], user['user'][cols[3]]))
            print_sorted_array(line_entries)
        else:
            print(colFormat % (cols[0], 'corp' + cols[1],
                               cols[2], cols[3]))
            for user in users['data']:
                line_entries.append(colFormat % (user[cols[0]], user[cols[1]],
                                                 user[cols[2]], user[cols[3]]))
        print_sorted_array(line_entries)


def do_list_membership(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)
    if args.email_id:
        memberships = api.get_memberships(args.email_id)
        cols = ['role', 'site']
        colFormat = "%10s %s"
        if memberships:
            line_entries = []
            print(colFormat % (cols[0], cols[1]))
            for member in memberships['data']:
                line_entries.append(colFormat % (member[cols[0]],
                                                 "%s [%s]" % (member[cols[1]]['displayName'],
                                                              member[cols[1]]['name'])))
            print_sorted_array(line_entries)


def do_add_user(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)

    input_file = resolve_input_file(args.file_name)
    location_string = 'corp'
    if args.site_name:
        api.site = args.site_name
        location_string = args.site_name

    if args.email_id:
        data = resolve_user_data_role(api, args.role_name)
        if args.dry_run:
            print("Adding %s to %s with %s role" %
                  (args.email_id, location_string, data['role']))
        add_new_user(api, args.email_id, args.role_name, args.api_user)
    if input_file:
        add_users_from_file(input_file, api, args, location_string)


def add_users_from_file(input_file, api, args, location_string):
    entries = 0
    with open_file_for_read(input_file) as f:
        line = f.readline()
        while line:
            cols = line.split(",")
            if len(cols) == 2:
                if args.role_name:
                    role = args.role_name
                else:
                    role = cols[1]
                data = resolve_user_data_role(api, role)
                args.role_name = cols[1]
                args.email_id = cols[0]

                if args.dry_run:
                    print("Adding %s to %s with %s role" %
                          (cols[0].strip(), location_string, data['role']))
                add_new_user(api, args.email_id,
                             args.role_name, args.api_user)

                entries += 1
            line = f.readline()
    print("Processed %d entries" % entries)


def do_remove_user(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)

    input_file = resolve_input_file(args.file_name)
    location_string = 'corp'
    if args.site_name:
        api.site = args.site_name
        location_string = args.site_name

    if args.email_id:
        if args.dry_run:
            print("Deleting %s from %s" % (args.email_id, location_string))
        else:
            if args.site_name:
                api.delete_site_member(args.email_id)
            else:
                api.delete_corp_user(args.email_id)
    if input_file:
        entries = 0
        with open_file_for_read(input_file) as f:
            line = f.readline()
            while line:
                if args.dry_run:
                    print("Deleting %s from %s" %
                          (line.strip(), location_string))
                else:
                    if args.site_name:
                        api.delete_site_member(line.strip())
                    else:
                        api.delete_corp_user(line.strip())
                entries += 1
                print(line)
                line = f.readline()
        print("Processed %d entries" % entries)


def resolve_user_data_role(api, user_role):
    valid_roles = ['admin', 'user', 'observer', 'owner']
    data = {'role': 'observer'}
    if not api.site:
        data['memberships'] = {'data': []}

    if user_role in valid_roles:
        data['role'] = user_role

    return data


def resolve_input_file(file_arg):
    if file_arg and file_arg == '-':
        return sys.stdin

    return file_arg


def open_file_for_read(file_arg):
    if isinstance(file_arg, str):
        return open(file_arg, 'r')
    return file_arg


def print_sorted_array(arg_list):
    if isinstance(arg_list, list):
        arg_list.sort()
        for arg in arg_list:
            print(arg)
