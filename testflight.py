import requests
import json

def login():
    url = 'https://idmsa.apple.com/appleauth/auth/signin?widgetKey=e0b80c3bf78523bfe80974d320935bfa30add02e1bff88ec2166c6bd5a706c42'
    payload = {
        "accountName": "example@icloud.com",
        "password": "password",
        "rememberMe": 'false'
    }
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/javascript'
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    if r.status_code == 200:
        print('Login Success')
    return r.cookies

def getFirstContentProviderId(cookie):
    url = "https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/ra/user/detail"
    res = requests.get(url, cookies=cookie)
    if res.status_code == 200:
        print('Content ProviderId get Success')
    data = res.json()
    accounts = data['data']['associatedAccounts']
    for acc in accounts:
        if acc['contentProvider']['name'] == 'Some Group Name':		#Provider name from your itunes account	
            return acc['contentProvider']['contentProviderId']
    return data['data']['associatedAccounts'][0]['contentProvider']['contentProviderId']

def getDefaultExternalGroupId(contentProviderId, appid, cookie):
    url = 'https://itunesconnect.apple.com/testflight/v2/providers/{teamId}/apps/{appId}/groups'.format(teamId=contentProviderId, appId=appid)
    resp = requests.get(url, cookies=cookie)
    if resp.status_code == 200:
        print('GroupId get Success')
    groups = resp.json()['data'];
    for group in groups:
        if group['name'] == 'Auto Beta Testers':	#Group name what you created in your itunes account.
            return group['id']
    return None
    # return "2574c871-3f69-497c-9694-3ce2185271a6"

def addTester(email, contentProviderId, appId, groupId, cookie, firstname='', lastname=''):
    params = {'email': email, 'firstName': firstname, 'lastName': lastname}
    url = 'https://itunesconnect.apple.com/testflight/v2/providers/{teamId}/apps/{appId}/testers'.format(teamId=contentProviderId, appId=appId)
    # print(url)
    r = requests.post(url, data=json.dumps(params), headers={'Content-Type': 'application/json'}, cookies=cookie)
    testerId = r.json()['data']['id']

    param = {
        "groupId": groupId,
        "testerId": testerId,
    }

    header = {
        "Content-Type": "application/json",
        "Origin": "https://itunesconnect.apple.com",
        "Pragma": "no-cache",
        "Referer": "https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/ra/ng/app/1126390498/testflight?section=group&subsection=testers&id=0948fa9f-8cd1-49f0-82cf-5ae46bae2d4b",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
        "X-Csrf-Itc": "itc"
    }

    url = 'https://itunesconnect.apple.com/testflight/v2/providers/{teamId}/apps/{appId}/groups/{groupId}/testers/{testerId}'.format(teamId=contentProviderId, appId=appId, groupId=groupId, testerId=testerId)
    url1 = 'https://itunesconnect.apple.com/testflight/v2/providers/{teamId}/apps/{appId}/groups/{groupId}/testers'.format(teamId=contentProviderId, appId=appId, groupId=groupId)
    
    res = requests.post(url1, data=json.dumps([params]), headers=header, cookies=cookie)
    print(res.status_code)
    resp = requests.put(url, data=json.dumps(param), headers={'Content-Type': 'application/json'}, cookies=cookie)
    print(resp.status_code)

def main():
    appid = "1126390498"		#Appid for your itunes App
    email = 'example@vajro.com'
    firstname = 'xxx'
    lastname = 'yyy'
    cookie = login()
    cookie_data = {}
    for x in cookie:
        cookie_data[x.name] = x.value
    contentProviderId = getFirstContentProviderId(cookie_data)
    groupId = getDefaultExternalGroupId(contentProviderId, appid, cookie_data)
    addTester(email, contentProviderId, appid, groupId, cookie_data, firstname, lastname)

main()