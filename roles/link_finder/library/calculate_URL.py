import urllib
try:
    import urllib2 as urllib_request
except ImportError:
    import urllib.request as urllib_request
import json
import os
import re

from ansible.module_utils.basic import *

'''
regex:
~~~~~~~~~~~~~~~~~~~~~~~
Cloud Agent and Server:
windows: .*expericloud.*.exe
mac: .*Cloud.*.dmg
~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~
Cloud Server no installer:
.*cloudaserver.*.zip
~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~
Cloud Agent no installer:
.*cloudagent.*.zip
~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~
Selenium:
windows: .*selenium_agent.*.exe
mac: .*selenium_agent.*.dmg 
~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~
Reporter:
windows: .*reporter_windows.*.exe
~~~~~~~~~~~~~~~~~~~~~~~
'''

def get_json_data(url, key):
    header = {'Accept': 'application/json'}
    req = urllib_request.Request(url, data=None, headers=header)
    response = urllib_request.urlopen(req)
    page = response.read()
    jdata = json.loads(page)
    return jdata[key]

def get_file_from_artifacts(artifacts, regex):
    for i in range(len(artifacts)):
        file_name = artifacts[i]['name']
        if re.match(regex, file_name):
            return artifacts[i]

def get_build(build_id, branch):
    baseurl = "http://192.168.1.213:8090"
    uri = "{}/guestAuth/app/rest/buildTypes/id:{}/builds/?locator=branch:{},status:SUCCESS,count:1"
    url = uri.format(baseurl, build_id, branch)
    builds = get_json_data(url, "build")
    return builds[0]

def get_artifact_by_build_uid(build_uid, regex_pattern):
    baseurl = "http://192.168.1.213:8090"
    uri = "{}/guestAuth/app/rest/builds/id:{}/artifacts/children/"
    url = uri.format(baseurl, build_uid)
    artifacts = get_json_data(url, "file")
    return get_file_from_artifacts(artifacts, regex_pattern)

def main():

    module = AnsibleModule(argument_spec=dict(
        build_id=dict(required=True),
        branch=dict(required=True),
        regex_pattern=dict(required=True)
    ))

    # module = {
    #     "params": {
    #         "build_id": "Cloud_CloudTrunk",
    #         "branch": "12.4",
    #         "regex_pattern": ".*Linux.*.zip"
    #     }
    # }

    build_id = module.params["build_id"]
    branch = module.params["branch"]
    regex_pattern = module.params["regex_pattern"]

    build = get_build(build_id, branch)
    # print(build)

    build_uid = build["id"]
    # print(build_uid)
    
    app_version = "{}.{}".format(build["branchName"], build["number"])
    # print(app_version)
    
    artifact = get_artifact_by_build_uid(build_uid, regex_pattern)
    # print(artifact)

    file_name = artifact["name"]

    base_url = "http://192.168.1.213:8090"
    download_url = "{}/guestAuth/app/rest/builds/id:{}/artifacts/content/{}".format(base_url, build_uid, file_name)

    module.exit_json(download_url=download_url, file_name=file_name, app_version=app_version)

if __name__ == '__main__':
    main()