#!/usr/bin/env python3
import os
import sys
from urllib.request import urlopen
import json
import time

def action_error(msg, status=1):
    print("::error::%s" % msg, flush=True)
    sys.exit(status)

def action_msg(msg):
    print(msg, flush=True)

def action_debug(msg):
    print("::debug::%s" % msg, flush=True)

def status(slug, key):
    url = "https://leanpub.com/%s/job_status?api_key=%s" % (slug, key)
    action_debug("Querying %s" % url)
    with urlopen(url) as resp:
        text = resp.read()
        data = json.loads(text)
        action_debug("Leanpub status: %s" % data)
        return data

def main():
    book_slug = sys.argv[1]
    if not book_slug:
        action_error("Missing argument: BOOK_SLUG")
    action_debug("book_slug=%s" % book_slug)

    api_key = os.environ['LEANPUB_API_KEY']
    action_msg("::add-mask::%s" % api_key)

    s = status(book_slug, api_key)
    prevstep = None
    if s == {}:
        action_msg("No Leanpub build running")

    while s != {}:
        if 'backtrace' in s:
            action_msg("::group::Leanpub error log")
            action_msg("Error! Backtrace:\n%s" % s['backtrace'])
            action_msg("::endgroup::")
            action_error("Leanpub build failure, see error backtrace above")

        step = s.get('message', s.get('msg'))
        if step != prevstep:
            action_msg("Step %s of %s: %s" % (s.get('num', 0), s.get('total', 0), step))
        prevstep = step

        # Exit as soon as the build is complete, don't wait for the next round
        if s['status'] == 'complete':
            break

        time.sleep(3)
        s = status(book_slug, api_key)

if __name__ == "__main__":
    main()
