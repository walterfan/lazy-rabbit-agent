import requests
import json

# Get the JWT token
def get_token(username, password, token_url):
    response = requests.post(token_url, data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to get token from {token_url} as {response.text}")
        return None

def get(url, params={}, accessToken="", tokenPrefix = 'Bearer '):
    get_headers = {}
    get_headers["Content-Type"] = "application/json"
    if accessToken:
        get_headers["Authorization"] = tokenPrefix + accessToken

    print("{}, {}".format(url, get_headers))

    response = requests.get(url, headers=get_headers, verify=False)

    content = ""
    if response.status_code >= 200 and response.status_code < 300:
        content = response.text
        #logger.info(str(json.dumps(results, indent=4, sort_keys=True)))
    else:
        print("get {} error, response code is {}: {}".format(url, response.status_code, response.text))

    return response.status_code, content

def post(url, post_headers={}, post_datas={}, accessToken=""):
    if accessToken:
        post_headers["Authorization"] = "Bearer " + accessToken
    print("{}, {}, {}".format(url, post_headers, post_datas))

    response = requests.post(url, headers=post_headers, data=json.dumps(post_datas), verify=False)

    content = ""
    if response.status_code >= 200 and response.status_code < 300:
        content = response.text
    else:
        print("get {} error, response code is {}: {}".format(url, response.status_code, response.text))
    return response.status_code, content