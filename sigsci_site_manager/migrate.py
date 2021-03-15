import json
import re
from copy import deepcopy

def get_dependency_items(item, found=None):
    if found is None:
        found = []
    if isinstance(item, dict):
        if any([x.startswith('corp.') for x in item.values() if isinstance(x, str)]):
            if item not in found:
                found.append(item)
        for k, v in item.items():
            if isinstance(v, (list, tuple, dict)):
                found.extend([x for x in get_dependency_items(v, found=found) if x not in found])
    elif isinstance(item, (list, tuple)):
        for i in item:
            found.extend([x for x in get_dependency_items(i, found=found) if x not in found])
    return found

def get_rule_dependencies(rule):
    dependencies = {'signal': set(), 'rule_list': set()}
    for item in get_dependency_items(rule):
        try:
            if item['operator'] == 'inList':
                dependencies['rule_list'].add(item['value'])
        except KeyError:
            pass
        try:
            if item['type'] == 'addSignal':
                dependencies['signal'].add(item['signal'])
        except KeyError:
            pass
    return dependencies

def get_corp_items(api):
    corp_items = {}
    corp_items['rule_list'] = {x['id']: x for x in 
                                    api.get_corp_rule_lists()['data']}
    corp_items['signal'] = {x['tagName']: x for x in 
                                api.get_corp_signals()['data']}
    return corp_items

def get_alert_dependencies(alert):
    if alert['tagName'].startswith('corp.'):
        return alert['tagName']

def get_advanced_rule_dependencies(advanced_rule):
    dependencies = {'rule_list': set(), 'signal': set()}
    matches = re.findall('[^\#]"(matchers|lists)*/*(corp\..+?)[")\s]',
                   str(advanced_rule))
    for match in matches:
        if match[0] in ['matchers', 'lists']:
            dependencies['rule_list'].add(match[1])
        else:
            dependencies['signal'].add(match[1])
    return dependencies

def format_dependencies(dependencies):
    # Improve readability of dependency lists
    items = []
    for item in dependencies:
        if dependencies[item]:
            items.append(f"'{item}': "
                         f"{', '.join([str(x) for x in dependencies[item]])}")
    return f"({', '.join(items)})"

def migrate(api, file_name, output_file, dest_corp, strip, keep_users):
    site_backup = json.load(open(file_name))
    new_site = deepcopy(site_backup)
    new_site['source']['corp'] = dest_corp
    corp_dependencies = {'signal': set(), 'rule_list': set()}

    # If not stripping dependencies, we need access to the same corp
    if site_backup['source']['corp'] != api.corp and not strip:
        raise Exception(
            "CORP must be the same as backup file, otherwise use --strip.")
    msg = f"Migrating '{file_name}' from corp={api.corp} to corp={dest_corp}."
    if strip:
        msg += " Stripping all items with corp-level dependencies."
    if keep_users:
        msg += " Preserving users."
    else:
        msg += " Stripping users."
    print(msg)
    
    # Drop users if param not set
    if not keep_users:
        new_site['site_members'] = []
    
    # Copy custom_alerts handling any corp dependencies
    print("\nMigrating custom alerts...")
    if strip:
        new_site['custom_alerts'] = []
    for alert in site_backup['custom_alerts']:
        dependency = get_alert_dependencies(alert)
        if dependency and not strip:
            corp_dependencies['signal'].add(dependency)
            print(f"  Migrating '{alert['longName']}' with corp signal "
                  f"dependency: {dependency}")
        elif not dependency:
            new_site['custom_alerts'].append(alert)
        else:
            print(f"  Skipping '{alert['longName']}' with corp signal "
                  f"dependency: {dependency}")

    # Copy site_rules handling any corp dependencies
    print("\nMigrating site rules...")
    if strip:
        new_site['site_rules'] = []
    for site_rule in site_backup['site_rules']:
        dependencies = get_rule_dependencies(site_rule)
        if any(dependencies.values()) and not strip:
            for dependency_type in dependencies:
                for dependency in dependencies[dependency_type]:
                    corp_dependencies[dependency_type].add(dependency)
            print(f"  Migrating '{site_rule['reason']}' with dependencies: "
                  f"{format_dependencies(dependencies)}")
        elif not any(dependencies.values()):
            new_site['site_rules'].append(site_rule)
        else:
            print(f"  Skipping '{site_rule['reason']}' with dependencies: "
                  f"{format_dependencies(dependencies)}")

    # Copy advanced_rules handling any corp dependencies
    print("\nMigrating advanced rules...")
    if strip:
        new_site['advanced_rules'] = []
    for advanced_rule in site_backup['advanced_rules']:
        dependencies = get_advanced_rule_dependencies(advanced_rule)
        if any(dependencies.values()) and not strip:
            for dependency_type in dependencies:
                for dependency in dependencies[dependency_type]:
                    corp_dependencies[dependency_type].add(dependency)
            print(f"  Migrating '{advanced_rule['shortName']}' with "
                  f"dependencies: {dependencies}")
        elif not any(dependencies.values()):
            new_site['advanced_rules'].append(advanced_rule)
        else:
            print(f"  Skipping '{advanced_rule['shortName']}' with "
                  f"dependencies: {dependencies}")

    # Add corp_items to new backup, if necessary    
    if any(corp_dependencies.values()):
        print("\nAdding corp items to backup...")
        corp_items = get_corp_items(api)
        new_site['corp_items'] = {x: [] for x in corp_dependencies 
            if corp_dependencies[x]}
        for dependency_type in corp_dependencies:
            new_site['corp_items'][dependency_type] = []
            for dependency in corp_dependencies[dependency_type]:
                try:
                    new_site['corp_items'][dependency_type].append(
                        corp_items[dependency_type][dependency])
                    print(f"  {dependency_type}/{dependency}")
                except KeyError:
                    print(f"  Existing broken dependency: {dependency_type}/"
                          f"{dependency}")

    if output_file is None:
        output_file = f"migrated_{file_name}"
    print(f"\nWriting {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(new_site, f)
