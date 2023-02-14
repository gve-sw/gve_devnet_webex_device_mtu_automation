# GVE DevNet Webex Device MTU Automation
This repository contains the code for a Python Flask app that pulls the Webex devices associated with an organization, displays those devices and their MTU values, and then pushes a new MTU value for the specified devices. The app accomplishes this by installing a macro, activating the macro, and then using the macro on the devices to change the MTU values. Note: this prototype is not capable of installing the macro on personal Webex devices. For the app to be able to change the MTU values of those devices, it would require the user to pre-emptively install and activate the macro on the personal device.

![/IMAGES/webex_device_mtu_automation_workflow.png](/IMAGES/webex_device_mtu_automation_workflow.png)

## Contacts
* Danielle Stacy
* Gerardo Chaves

## Solution Components
* Python 3.10
* Flask
* Webex Devices
* Webex Macros
* Javascript

## Prerequisites
**OAuth Integrations**: Integrations are how you request permission to invoke the Webex REST API on behalf of another Webex Teams user. To do this in a secure way, the API supports the OAuth2 standard which allows third-party integrations to get a temporary access token for authenticating API calls instead of asking users for their password. To register an integration with Webex Teams:
1. Log in to `developer.webex.com`
2. Click on your avatar at the top of the page and then select `My Webex Apps`
3. Click `Create a New App`
4. Click `Create an Integration` to start the wizard
5. Follow the instructions of the wizard and provide your integration's name, description, and logo
6. After successful registration, you'll be taken to a different screen containing your integration's newly created Client ID and Client Secret
7. Copy the secret and store it safely. Please note that the Client Secret will only be shown once for security purposes
8. Note that access token may not include all the scopes necessary for this prototype by default. To include the necessary scopes, select `My Webex Apps` under your avatar once again. Then click on the name of the integration you just created. Scroll down to the `Scopes` section. From there, select all the scopes needed for this integration (spark-admin:devices_read and spark:xapi_commands)

> To read more about Webex Integrations & Authorization and to find information about the different scopes, you can find information [here](https://developer.webex.com/docs/integrations)

## Installation/Configuration
1. Clone this repository with `git clone [repository name]`
2. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/). Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).
3. Install the requirements with the command `pip3 install -r requirements.txt`.
4. Add the Client ID and Client Secret to the environment variables in the .env file.
```
CLIENT_ID = "enter client id here"
CLIENT_SECRET = "enter client secret here"
```


## Usage
To start the web app, use the command:
```
$ flask run
```

Then access the app in your browser of choice at the address `http://127.0.0.1:5000`. From here, you will be asked to login to the web app with your Webex account that you created the Webex integration with.

![/IMAGES/login_prompt.png](/IMAGES/login_prompt.png)

![/IMAGES/webex_login.png](/IMAGES/webex_login.png)

Once you have gone through the login process, you will be redirected to page where MTU values are displayed. On this page, it displays the device name, product type, mode of the device (organizational or personal), the IP address, and the current MTU size. The last column of the table provides a field to enter a new MTU value for the device. To implement these changes, hit the Apply Changes button at the top of the table.

![/IMAGES/main_page.png](/IMAGES/main_page.png)

![/IMAGES/change_mtu.png](/IMAGES/change_mtu.png)

![/IMAGES/updated_mtu.png](/IMAGES/updated_mtu.png)

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
