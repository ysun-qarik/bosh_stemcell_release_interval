# importing the requests library
import os
import requests
import sys

from collections import defaultdict
from datetime import datetime, timezone, timedelta


def isReleaseNeedToLookAt(release):
    return release['draft'] == False and 'stable' not in release['tag_name']


if __name__ == '__main__':
    DT_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    URL = "https://api.github.com/repos/cloudfoundry/bosh-linux-stemcell-builder/releases"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    USER = os.getenv('GITHUB_USER')
    PASSWORD = os.environ.get('GITHUB_PASSWORD')

    if USER == '' or PASSWORD == '':
        print('ENVVAR is missing: GITHUB_USER and GITHUB_PASSWORD')
        sys.exit()
    auth = (USER, PASSWORD)

    perPage = 100
    page = 0
    releases = defaultdict(list)
    # extracting data in json format
    data = ['']
    while data != []:
        PARAMS = {'per_page': perPage, 'page': page}
        r = requests.get(url=URL, params=PARAMS, auth=auth)
        data = r.json()
        if 'message' in data != None:
            msg = data['message']
            print(f'Ops: {msg}')
            break
        for release in data:
            if isReleaseNeedToLookAt(release):
                created_at = release['published_at']
                createdAtDT = datetime.strptime(created_at, DT_FORMAT)
                tagName = release['tag_name']
                releasesOSCodeName = tagName.split('/')[0]
                releases[releasesOSCodeName].append(createdAtDT)
        page += 1

    release_interval = defaultdict(list)
for k, v in releases.items():
    print(k)
    t = None
    for dt in v:
        if t == None:
            t = dt
            continue
        delta = t-dt
        if delta > timedelta(days=0):
            release_interval[k].append(t-dt)
        t = dt
    print(sum(release_interval[k], timedelta())/len(release_interval[k]))
