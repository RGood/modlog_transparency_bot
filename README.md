# Prerequisites

* Have python3 and pip installed

# Usage:

1. Copy info_template.ini
2. Rename to `info.ini`
3. Go to https://reddit.com/prefs/apps
4. Hit `create another app...` at the bottom
5. Give it whatever name / description you want, select `script`, and copy the `redirect` field in info.ini to the `redirect uri` field
6. Copy the `id` and `secret` to info.ini in the [App] section
7. [Optional] Add the account `username` and `password` of the acount you're running the bot on to the info.ini file. If you don't, you can still authenticate with oauth2
8. Run `pip3 install -r requirements.txt`
9. Run `python3 src/main.py`
