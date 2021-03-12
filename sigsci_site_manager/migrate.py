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
    dependencies = []
    matches = re.findall('[^\#]"(matchers|lists)*/*(corp\..+?)[")\s]',
                   str(advanced_rule))
    for match in matches:
        if match[0] in ['matchers', 'lists']:
            dependencies.append({'type': 'rule_list', 'value': match[1]})
        else:
            dependencies.append({'type': 'signal', 'value': match[1]})
    return dependencies

def migrate(api, file_name, output_file, dest_corp, strip, keep_users):
    site_backup = json.load(open(file_name))
    new_site = deepcopy(site_backup)
    new_site['source']['corp'] = dest_corp
    corp_dependencies = {'signal': set(), 'rule_list': set()}

    # If not stripping dependencies, we need access to the same corp
    if site_backup['source']['corp'] != api.corp and not strip:
        raise Exception(
            "CORP must be the same as backup file, otherwise use --strip.")
    
    msg = "Migrating '{}' from corp={} to corp={}.".format(
        file_name, api.corp, dest_corp)
    if strip:
        msg += " Stripping all items with corp-level dependencies."
    if keep_users:
        msg += " Preserving users."
    print(msg)
    
    # Drop users if param not set
    if not keep_users:
        new_site['site_members'] = []
    
    # Copy custom_alerts handling any corp dependencies
    if strip:
        new_site['custom_alerts'] = []
    for alert in site_backup['custom_alerts']:
        dependency = get_alert_dependencies(alert)
        if dependency and not strip:
            corp_dependencies['signal'].add(dependency)
        elif not dependency:
            new_site['custom_alerts'].append(alert)

    # Copy site_rules handling any corp dependencies
    if strip:
        new_site['site_rules'] = []
    for site_rule in site_backup['site_rules']:
        dependencies = get_rule_dependencies(site_rule)
        if dependencies and not strip:
            for dependency_type in dependencies:
                for dependency in dependencies[dependency_type]:
                    corp_dependencies[dependency_type].add(dependency)
        elif not dependencies:
            new_site['site_rules'].append(site_rule)

    # Copy advanced_rules handling any corp dependencies
    if strip:
        new_site['advanced_rules'] = []
    for advanced_rule in site_backup['advanced_rules']:
        dependencies = get_advanced_rule_dependencies(advanced_rule)
        if dependencies and not strip:
            for dependency in dependencies:
                corp_dependencies[dependency['type']].add(dependency['value'])
        elif not dependencies:
            new_site['advanced_rules'].append(advanced_rule)

    # Add corp_items to new backup, if necessary
    if any(corp_dependencies.values()):
        corp_items = get_corp_items(api)
        new_site['corp_items'] = {x: [] for x in corp_dependencies if corp_dependencies[x]}
        for dependency_type in corp_dependencies:
            new_site['corp_items'][dependency_type] = []
            for dependency in set(corp_dependencies[dependency_type]):
                try:
                    new_site['corp_items'][dependency_type].append(corp_items[dependency_type][dependency])
                except KeyError:
                    print("Existing broken dependency: {} > {}".format(dependency_type, dependency))

    if output_file is None:
        "migrated_{}".format(file_name)
    with open(output_file, 'w') as f:
        json.dump(new_site, f)
