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
            print(colFormat % (cols[0], 'site-' + cols[1],
                               cols[2], cols[3]))
            for user in users['data']:
                line_entries.append(colFormat % (user['user'][cols[0]], user[cols[1]],
                                                 user['user'][cols[2]], user['user'][cols[3]]))
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
            for member in memberships['data']:
                line_entries.append(colFormat % (member[cols[0]],
                                                 "%s [%s]" % (member[cols[1]]['displayName'],
                                                              member[cols[1]]['name'])))
            if len(line_entries) > 0:
                print(colFormat % (cols[0], cols[1]))
                print_sorted_array(line_entries)


def do_add_user(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)

    input_file = resolve_input_file(args.file_name)
    location_string = 'corp'
    if args.site_name:
        api.site = args.site_name
        location_string = args.site_name

    user_list = []
    if args.email_id:
        user_list.append([args.email_id, args.role_name])
    if input_file:
        user_list = get_users_from_file(input_file, 2)

    added_users = 0
    for entry in user_list:
        user_role = entry[1]
        if args.role_name and len(entry[1]) >= 0:
            user_role = args.role_name
        data = resolve_user_data_role(api, user_role)
        if args.dry_run:
            print("Adding %s to %s with %s role" %
                  (entry[0], location_string, data['role']))
        add_new_user(api, entry[0], data['role'], args.api_user)
        added_users += 1
    print("Added %d users" % added_users)


def do_remove_user(args):
    api = init_api(args.username, args.password, args.token, args.corp,
                   args.dry_run)

    input_file = resolve_input_file(args.file_name)
    location_string = 'corp'
    if args.site_name:
        api.site = args.site_name
        location_string = args.site_name

    user_list = []
    if args.email_id:
        user_list.append([args.email_id])
    if input_file:
        user_list = get_users_from_file(input_file, 1)

    removed_users = 0
    for entry in user_list:
        if args.dry_run:
            print("Removing %s from %s" %
                  (entry[0], location_string))
        remove_user(api, entry[0])
        removed_users += 1
    print("Removed %d users" % removed_users)


def remove_user(api, email_id):
    if api.site:
        api.delete_site_member(email_id)
    else:
        api.delete_corp_user(email_id)


def resolve_user_data_role(api, user_role):
    valid_roles = ['admin', 'user', 'observer', 'owner']
    data = {'role': 'observer'}
    if not api.site:
        data['memberships'] = {'data': []}

    if user_role in valid_roles:
        data['role'] = user_role

    return data


def get_users_from_file(input_file, num_attrs):
    # This may be memory bound for a large number of users
    list_users = []
    with open_file_for_read(input_file) as f:
        line = f.readline()
        while line:
            cols = line.split(",")
            num_cols = len(cols)
            cur_cols = []
            for i in range(0, num_attrs):
                if i < num_cols:
                    cur_cols.append(cols[i].strip())
                else:
                    cur_cols.append('')
            list_users.append(cur_cols)
            line = f.readline()
    return list_users


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
