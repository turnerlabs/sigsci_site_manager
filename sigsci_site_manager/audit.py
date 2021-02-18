import os
import json
import re

def get_site_custom_alerts(api, site, active_only=False):
    alerts = []
    api.site = site
    for alert in api.get_custom_alerts()['data']:
        if alert['type'] == 'siteAlert':
            if (active_only and alert['enabled']) or (not active_only):
                alerts.append(alert)
    return alerts

def create_audit_ref(alerts):
    ''' Create a baseline compliance reference. Any (x.y.z) values contained in
        an alert's longName value will be interpreted as indicating that alert
        confers compliance with the referenced section of the baseline.
        ie - an alert named "(1.2) FooBar" will be assumed to grant compliance
        with baseline section 1.2
    '''
    audit_ref = {}
    for alert in alerts:
        matches = re.findall("\(((\d+\.)?(\d+\.)?(\*|\d+))\)", alert['longName'])
        for match in matches:
            try:
                audit_ref[alert['tagName']].add(match[0])
            except KeyError:
                audit_ref[alert['tagName']] = set([match[0]])
    return {x: tuple(audit_ref[x]) for x in audit_ref}

def audit(site, baseline_ref):
    compliance_ref = {'OTHER': []}
    if baseline is None:
        if os.path.isfile('audit_baseline.json'):
            baseline = json.load(open('audit_baseline.json'))
        else:
            raise Exception("A baseline is required.")
    else:
        baseline = create_audit_dict(get_site_custom_alerts(baseline))
    for sections in baseline.values():
        for section in sections:
            compliance_ref[section] = []
    audit_site_alerts = get_site_custom_alerts(site)
    for alert in audit_site_alerts:
        try:
            for section in baseline[alert['tagName']]:
                compliance_ref[section].append((alert['tagName'], alert['longName']))
        except KeyError:
            compliance_ref['OTHER'].append((alert['tagName'], alert['longName']))
    return compliance_ref
