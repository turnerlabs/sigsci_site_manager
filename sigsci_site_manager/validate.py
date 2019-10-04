import time
import uuid

import requests

from sigsci_site_manager.__version__ import __version__

HEADER = "X-SigSci-Site-Manager-Test-Id"

DEFAULT_TEST_CASES = [
    {
        "verb": "GET",
        "path": "/?<script>alert('test');</script>",
        "body": None
    }
]


def validate(api, site, hostname, dry_run, test_cases=None):
    print("Validating deployment of site '%s'" % site)

    api.site = site

    nonces = []

    if not test_cases:
        test_cases = DEFAULT_TEST_CASES

    print("Running test cases...")
    for test_case in test_cases:
        nonce = str(uuid.uuid4())
        nonces.append(nonce)
        try:
            run_test_case(hostname, test_case, nonce, dry_run)
        except requests.exceptions.RequestException:
            print("  Error sending request")

    print("Waiting for SigSci agent to upload request logs...")
    if not dry_run:
        time.sleep(30)

    success = search_requests_log_all(api, site, nonces)

    if not dry_run:
        if success:
            print("Success")
        else:
            print("Failed")


def run_test_case(hostname, test_case, nonce, dry_run):
    print(" %s: %s %s" %
          (nonce, test_case["verb"], test_case["path"]))
    if dry_run:
        return

    headers = {
        "User-Agent": "sigsci_site_manager/%s" % __version__,
        HEADER: nonce
    }

    if test_case["verb"] == "GET":
        requests.get("%s%s" % (hostname, test_case["path"]), headers=headers)
    elif test_case["verb"] == "POST":
        requests.post("%s%s" % (hostname, test_case["path"]),
                      headers=headers,
                      body=test_case["body"])


def search_requests_log_all(api, site, nonces):
    print("Searching request log...")

    r = api.get_requests(parameters={"q": "from:-1min"})
    if not r:
        return False

    success = True
    for nonce in nonces:
        if not search_requests_log(r.get("data", []), nonce):
            success = False
    return success


def search_requests_log(data, nonce):
    print(" %s..." % nonce)

    for item in data:
        for header in item["headersIn"]:
            if header == [HEADER, nonce]:
                print(" Matched test case %s with request %s" %
                      (nonce, item["id"]))
                return True

    print(" Failed to find test case %s in request log" % nonce)
    return False
