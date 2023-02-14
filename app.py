#!/usr/bin/env python3
"""
Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
from flask import Flask, render_template, request, url_for, redirect, session, jsonify, make_response
from requests_oauthlib import OAuth2Session
from collections import defaultdict
import datetime
import time
import sys, requests, json, os
from webexteamssdk import WebexTeamsAPI
from itertools import islice
from dotenv import load_dotenv
from pprint import pprint

def get_devices(token):
    url = "https://webexapis.com/v1/devices"
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
        }
    response = requests.get(url, headers=headers)

    devices = json.loads(response.text)["items"]

    return devices


def install_macro(token, device_id):
    url = "https://webexapis.com/v1/xapi/command/Macros.Macro.Save"

    payload = json.dumps({
    "deviceId": device_id,
    "arguments": {
        "Name": "MTUSetter",
        "Overwrite": "True",
        "Transpile": "True"
    },
    "body": "import xapi from 'xapi';\nxapi.Event.Message.Send.on(event => {\nconsole.log(event);\nconst msg_words=event.Text.split(':');\n if (msg_words.length>1 && msg_words[0]=='SetMTU') {\n  xapi.Config.Network[1].MTU.set(parseInt(msg_words[1]));\n }\n });"
    })
    headers = {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def activate_macro(token, device_id):
    url = "https://webexapis.com/v1/xapi/command/Macros.Macro.Activate"

    payload = json.dumps({
        "deviceId": device_id,
        "arguments": {
            "Name": "MTUSetter"
        }
    })
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def get_mtu(token, device_id):
    url = "https://webexapis.com/v1/deviceConfigurations?deviceId=" + device_id + "&key=Network%5B1%5D.MTU"
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)

    mtu_value = json.loads(response.text)["items"]["Network[1].MTU"]["value"]

    return mtu_value


def set_mtu(token, device_id, mtu_value):
    url = "https://webexapis.com/v1/xapi/command/Message.Send"

    payload = json.dumps({
        "deviceId": device_id,
        "arguments": {
            "Text": "SetMTU:" + mtu_value
        }
    })
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


# Methods
# Returns location and time of accessing device
def getSystemTimeAndLocation():
    # request user ip
    userIPRequest = requests.get('https://get.geojs.io/v1/ip.json')
    userIP = userIPRequest.json()['ip']

    # request geo information based on ip
    geoRequestURL = 'https://get.geojs.io/v1/ip/geo/' + userIP + '.json'
    geoRequest = requests.get(geoRequestURL)
    geoData = geoRequest.json()

    #create info string
    location = geoData['country']
    timezone = geoData['timezone']
    current_time=datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    timeAndLocation = "System Information: {}, {} (Timezone: {})".format(location, current_time, timezone)


    return timeAndLocation


#Read data from json file
def getJson(filepath):
	with open(filepath, 'r') as f:
		json_content = json.loads(f.read())
		f.close()

	return json_content


#Write data to json file
def writeJson(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f)
    f.close()



# load all environment variables
load_dotenv()
# WEBEX_TOKEN = os.environ["WEBEX_TOKEN"]

# Global variables
AUTHORIZATION_BASE_URL = "https://api.ciscospark.com/v1/authorize"
TOKEN_URL = "https://api.ciscospark.com/v1/access_token"
# SCOPE = "[spark:xapi_statuses spark:xapi_commands spark-admin:devices_read spark-admin:devices_write]"
SCOPE = "spark-admin:devices_read spark:xapi_commands"
PUBLIC_URL = "http://127.0.0.1:5000"
REDIRECT_URI = ""

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

app.secret_key = '123456789012345678901234'

AppAdminID=''

##Routes
#Instructions
#Index
@app.route('/')
def login():
    return render_template('login.html')

@app.route("/callback", methods=["GET"])
def callback():
    """
    Retrieving an access token.
    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    global REDIRECT_URI

    print(session)
    print("oauth_state: {}".format(session['oauth_state']))
    print("Came back to the redirect URI, trying to fetch token....")
    print("redirect URI should still be: ",REDIRECT_URI)
    print("Calling OAuth2SEssion with CLIENT_ID ",os.getenv('CLIENT_ID')," state ",session['oauth_state']," and REDIRECT_URI as above...")
    auth_code = OAuth2Session(os.getenv('CLIENT_ID'), state=session['oauth_state'], redirect_uri=REDIRECT_URI)
    print("Obtained auth_code: ",auth_code)
    print("fetching token with TOKEN_URL ",TOKEN_URL," and client secret ",os.getenv('CLIENT_SECRET')," and auth response ",request.url)
    token = auth_code.fetch_token(token_url=TOKEN_URL, client_secret=os.getenv('CLIENT_SECRET'),
                                  authorization_response=request.url)

    print("Token: ",token)
    print("should have grabbed the token by now!")
    session['oauth_token'] = token
    with open('tokens.json', 'w') as json_file:
        json.dump(token, json_file)
    return redirect(url_for('.mtu'))

#manual refresh of the token
@app.route('/refresh', methods=['GET'])
def webex_teams_webhook_refresh():

    r_api=None

    teams_token = session['oauth_token']

    # use the refresh token to
    # generate and store a new one
    access_token_expires_at=teams_token['expires_at']

    print("Manual refresh invoked!")
    print("Current time: ",time.time()," Token expires at: ",access_token_expires_at)
    refresh_token=teams_token['refresh_token']
    #make the calls to get new token
    extra = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'refresh_token': refresh_token,
    }
    auth_code = OAuth2Session(os.getenv('CLIENT_ID'), token=teams_token)
    new_teams_token=auth_code.refresh_token(TOKEN_URL, **extra)
    print("Obtained new_teams_token: ", new_teams_token)
    #store new token

    teams_token=new_teams_token
    session['oauth_token'] = teams_token
    #store away the new token
    with open('tokens.json', 'w') as json_file:
        json.dump(teams_token, json_file)

    #test that we have a valid access token
    r_api = WebexTeamsAPI(access_token=teams_token['access_token'])

    return ("""<!DOCTYPE html>
                   <html lang="en">
                       <head>
                           <meta charset="UTF-8">
                           <title>Webex Teams Bot served via Flask</title>
                       </head>
                   <body>
                   <p>
                   <strong>The token has been refreshed!!</strong>
                   </p>
                   </body>
                   </html>
                """)

@app.route('/mtu', methods=['GET', 'POST'])
def mtu():
    try:
        global REDIRECT_URI
        global PUBLIC_URL
        global ACCESS_TOKEN

        if os.path.exists('tokens.json'):
            with open('tokens.json') as f:
                tokens = json.load(f)
        else:
            tokens = None

        if tokens == None or time.time()>(tokens['expires_at']+(tokens['refresh_token_expires_in']-tokens['expires_in'])):
            # We could not read the token from file or it is so old that even the refresh token is invalid, so we have to
            # trigger a full oAuth flow with user intervention
            REDIRECT_URI = PUBLIC_URL + '/callback'  # Copy your active  URI + /callback
            print("Using PUBLIC_URL: ",PUBLIC_URL)
            print("Using redirect URI: ",REDIRECT_URI)
            teams = OAuth2Session(os.getenv('CLIENT_ID'), scope=SCOPE, redirect_uri=REDIRECT_URI)
            authorization_url, state = teams.authorization_url(AUTHORIZATION_BASE_URL)

            # State is used to prevent CSRF, keep this for later.
            print("Storing state: ",state)
            session['oauth_state'] = state
            print("root route is re-directing to ",authorization_url," and had sent redirect uri: ",REDIRECT_URI)
            return redirect(authorization_url)
        else:
            # We read a token from file that is at least younger than the expiration of the refresh token, so let's
            # check and see if it is still current or needs refreshing without user intervention
            print("Existing token on file, checking if expired....")
            access_token_expires_at = tokens['expires_at']
            if time.time() > access_token_expires_at:
                print("expired!")
                refresh_token = tokens['refresh_token']
                # make the calls to get new token
                extra = {
                    'client_id': os.getenv('CLIENT_ID'),
                    'client_secret': os.getenv('CLIENT_SECRET'),
                    'refresh_token': refresh_token,
                }
                auth_code = OAuth2Session(os.getenv('CLIENT_ID'), token=tokens)
                new_teams_token = auth_code.refresh_token(TOKEN_URL, **extra)
                print("Obtained new_teams_token: ", new_teams_token)
                # assign new token
                tokens = new_teams_token
                # store away the new token
                with open('tokens.json', 'w') as json_file:
                    json.dump(tokens, json_file)


            session['oauth_token'] = tokens
            print("Using stored or refreshed token....")
            WEBEX_TOKEN=tokens['access_token']

        # submitting form to change MTU of devices
        if request.method == "POST":
            form_dict = request.form.to_dict()
            # check which devices have non-empty mtu size fields
            for device in form_dict:
                if form_dict[device] != "":
                    mtu_size = form_dict[device]
                    install_macro(WEBEX_TOKEN, device) # install the macro to change mtu size on the device
                    activate_macro(WEBEX_TOKEN, device) # activate the macro on the device
                    set_mtu(WEBEX_TOKEN, device, mtu_size) # use the macro to change the mtu size

            time.sleep(3)

        # the following code is used to render the web page
        display_devices = []
        devices = get_devices(WEBEX_TOKEN) # get all devices in the Webex org
        # iterate through the devices and get the id, display name, product name, and ip address of connected device
        for device in devices:
            if device["connectionStatus"] == "connected" or device["connectionStatus"] == "connected_with_issues":
                device_mtu = get_mtu(WEBEX_TOKEN, device["id"])
                device_id = device["id"]
                device_name = device["displayName"]
                product = device["product"]
                device_ip = device["ip"]
                # if a person is associated with the device, then it is a personal device, otherwise it belongs to the org and can have the macro installed remotely
                if "personId" in device.keys():
                    device_mode = "personal"
                else:
                    device_mode = "organizational"

                # create a dictionary with the relevant information to be displayed on the web page
                display_device = {
                    "displayName": device_name,
                    "product": product,
                    "ip": device_ip,
                    "mtu": device_mtu,
                    "mode": device_mode,
                    "id": device_id
                }
                display_devices.append(display_device) # the display_devices contains all the information for each connected device

        #Page without error message and defined header links
        return render_template('mtu.html', hiddenLinks=False, timeAndLocation=getSystemTimeAndLocation(), devices=display_devices)
    except Exception as e:
        print(e)
        #OR the following to show error message
        return ("""<!DOCTYPE html>
                   <html lang="en">
                       <head>
                           <meta charset="UTF-8">
                           <title>Webex Device MTU Automation</title>
                       </head>
                   <body>
                   <p>
                   <strong>There was an error retrieving and displaying the information!!</strong>
                   <br>
                   Error: {}
                   </p>
                   </body>
                   </html>
                """.format(e))
