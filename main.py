# importing the requests library
import json
import os
import requests
import sys

from collections import defaultdict
from datetime import datetime, timezone, timedelta
import numpy as np


def isReleaseNeedToLookAt(repo, release):
    repoSpecific = True
    if repo == 'bosh-linux-stemcell-builder':
        repoSpecific = not release['tag_name'].startswith('v')
    return release['draft'] == False and 'stable' not in release['tag_name'] and repoSpecific

def getReleaseName(repo,release):
    if repo =='cflinuxfs3':
        tagName = repo
    elif repo == 'binary-buildpack':
        tagName = repo
    elif repo == 'go-buildpack':
        tagName = repo
    elif repo == 'hwc':
        tagName = repo
    elif repo == 'java-buildpack':
        tagName = repo
    elif repo == 'dotnet-core-buildpack':
        tagName = 'dotnet-core-buildpack-' + release['tag_name'].split('.')[0]
    elif repo == 'nodejs-buildpack':
        tagName = repo
    elif repo =='php-buildpack':
        tagName = repo
    elif repo =='python-buildpack':
        tagName = repo
    elif repo =='r-buildpack':
        tagName = repo
    elif repo =='ruby-buildpack':
        tagName = repo
    elif repo =='staticfile-buildpack':
        tagName = repo
    else:
        tagName = release['tag_name']
    return tagName

def printCVSHeaders():
    print(';'.join(['release','sampleSize','avg','95%','90%','min','max','maxIgnoreOldRelease']))

def printCVS(releaseName,releaseInterval):
    avg = 0 if len(releaseIntervals[k]) == 0 else sum(releaseIntervals[k], timedelta())/len(releaseIntervals[k])
    avg95 = 0 if len(releaseIntervals[k]) == 0 else np.percentile(releaseIntervals[k], 95)
    avg90 = 0 if len(releaseIntervals[k]) == 0 else np.percentile(releaseIntervals[k], 90)
    minValue = 0 if len(releaseIntervals[k]) == 0 else min([dt for dt in releaseIntervals[k] if dt > timedelta(hours=1)])
    maxValue = 0 if len(releaseIntervals[k]) == 0 else max(releaseIntervals[k])
    maxIgnoreOldRelease = 0 if len(releaseIntervals[k]) == 0 else max([dt for dt in releaseIntervals[k] if dt < timedelta(days=100)])
    print(';'.join(map(str, [releaseName,len(releaseInterval[k]),avg,avg95,avg90,minValue,maxValue,maxIgnoreOldRelease])))



if __name__ == '__main__':
    SAVE_JSON_TO_FILE =     False
    READ_JSON_FROM_FILE =     True
    repos = ['nodejs-buildpack']#'bosh-linux-stemcell-builder','cflinuxfs3','binary-buildpack','go-buildpack','hwc', 'java-buildpack', 'dotnet-core-buildpack','nodejs-buildpack','php-buildpack','python-buildpack','r-buildpack', 'ruby-buildpack','staticfile-buildpack' ] #
    for repo in repos:
        DT_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
        URL = f"https://api.github.com/repos/cloudfoundry/{repo}/releases"
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
            if READ_JSON_FROM_FILE:
                with open(f'{repo}-data-{perPage}-{page}.json') as json_file:
                    data = json.load(json_file)
            else:
                r = requests.get(url=URL, params=PARAMS)
                data = r.json()
            if SAVE_JSON_TO_FILE:
                with open(f'{repo}-data-{perPage}-{page}.json', 'w') as f:
                    json.dump(data,f)

            if 'message' in data != None:
                msg = data['message']
                print(f'Ops: {msg}')
                break

            for release in data:
                if isReleaseNeedToLookAt(repo, release):
                    published_at = release['published_at']
                    publishedAtDT = datetime.strptime(published_at, DT_FORMAT)
                    tagName = getReleaseName(repo,release)

                    releasesOSCodeName = tagName.split('/')[0]
                    releases[releasesOSCodeName].append(publishedAtDT)
                    print(f'{published_at} {tagName} {release["tag_name"]}')
            page += 1
        
        releaseIntervals = defaultdict(list)
        
        for k, v in releases.items():
            t = None
            for dt in v:
                if t == None:
                    t = dt
                    continue

                delta = t-dt
                if delta:
                    releaseIntervals[k].append(t-dt)
                t = dt
            printCVS(k,releaseIntervals)
            # print(f'====={k}=====')
            # print(f'data based on {len(releases[k])} releases')

            # if len(releaseIntervals[k]) > 0:
            #     print(f'average: {sum(releaseIntervals[k], timedelta())/len(releaseIntervals[k])}')
            #     print(f'min: {min([dt for dt in releaseIntervals[k] if dt > timedelta(hours=1)])}')
            #     # there is cases the release interval takes longger than 300days, there cases happened
            #     # at the first few release
            #     print(f'max: {max(releaseIntervals[k])}')
            #     print(f'max(ignore>356 days): {max([dt for dt in releaseIntervals[k] if dt < timedelta(days=356)])}')


