# oauth PRAW template by /u/The1RGood #
#==================================================Imports=========================================================
import praw
import webbrowser
from flask import Flask, request
from threading import Thread
from configparser import ConfigParser
from lib.InviteAcceptor import InviteAcceptor
from lib.ModLogger import ModLogger
from collections import defaultdict
import traceback

#============================================Basic Config Params===================================================
config = ConfigParser()
config.read('info.ini')

username = config['Login']['username']
password = config['Login']['password']

scope = ['modconfig', 'subscribe', 'structuredstyles', 'mysubreddits', 'submit', 'modlog', 'save', 'read', 'privatemessages', 'identity', 'account', 'edit', 'modself'] #SET THIS.
#SEE http://praw.readthedocs.org/en/latest/pages/oauth.html#oauth-scopes FOR DETAILS ON SCOPE.
#These permissions should be enough, though.
#=============================================Advanced Config Params===============================================
#==================================================End Config======================================================

app = Flask(__name__)

#Kill function, to stop server once auth is granted
def kill():
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()
	return "Shutting down..."

#Callback function to receive auth code
@app.route('/authorize_callback')
def authorized():
	global access_information
	state = request.args.get('state', '')
	code = request.args.get('code', '')
	r.auth.authorize(code)
	user = r.user.me()
	text = 'Bot successfully started on account /u/'+user.name
	kill()
	return text

#==================================================OAUTH APPROVAL==================================================
r = None

#If login is configured with info.ini, use it otherwise open an oauth webpage flow

#If you only have command-line access to the host, you must add bot login to the info.ini
open_access_page = False

if(username != None and username != "" and password != None and password != ""):
    r = praw.Reddit(
    	client_id=config["App"]["id"],
    	client_secret=config["App"]["secret"],
    	user_agent="Public Modlog Bot",
    	username=username,
    	password=password
    )
else:
    r = praw.Reddit(
    	client_id=config["App"]["id"],
    	client_secret=config["App"]["secret"],
    	user_agent="Public Modlog Bot",
    	redirect_uri = config["App"]["redirect"]
    	#username=config["Login"]["username"],
    	#password=config["Login"]["password"]
    )

    if(open_access_page):
    	webbrowser.open(r.auth.url(scope, "UniqueKey"))
    else:
    	print("Follow this address to grant access: ")
    	print(r.auth.url(scope, "UniqueKey"))

    app.run(debug=False, port=6500)
#=====================================================================================================================
# MAIN LOGIC
target_subs = {}
ignored_users = defaultdict(lambda: [])
def update_targets(key_sub, val_sub):
    target_subs[key_sub] = val_sub
    updating = True

    #This logic is supposed to gracefully handle process-termination during file-writing
    while(updating):
        file_content = "\n".join(map(lambda key: "{0},{1}".format(key, target_subs[key]),target_subs.keys()))
        f = open('logging map.csv', 'w')
        try:
            f.write(file_content)
            f.close()
            updating = False
        except KeyboardInterrupt:
            f.close()

def main():
    running = True
    try:
        file = open('logging map.csv', 'r')
        for line in file:
            parts = line.split(',')
            if(len(parts) >= 2):
                target_subs[parts[0].lower()] = parts[1].lower()
                ignored_users[parts[0].lower()] = list(map(lambda x: x.lower().strip(), parts[2:]))
        file.close()
    except FileNotFoundError:
        pass

    ia = InviteAcceptor(reddit=r, target_subs=target_subs, sub_created_cb=update_targets)
    iaThread = Thread(target = ia.run, args=(), daemon=True)
    iaThread.start()

    ml = ModLogger(reddit=r, target_map=target_subs, ignored_users=ignored_users)
    while(running):
        try:
            ml.run()
        except KeyboardInterrupt:
            running = False
        except Exception as e:
            traceback.print_exc()

if __name__ == '__main__':
    main()
