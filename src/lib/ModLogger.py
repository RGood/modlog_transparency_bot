import praw
from collections import defaultdict
import traceback

class ModLogger():
	def __init__(self, reddit, subreddit_name="mod", target_map={}, ignored_users=defaultdict(lambda: [])):
		SMS = praw.models.reddit.subreddit.SubredditModerationStream
		sub = reddit.subreddit(subreddit_name)
		self.reddit = reddit
		self.data_stream = SMS(sub)
		self.target_map = target_map
		self.ignored_users = ignored_users

	def kill(self):
		self.running = False

	def update_target_map(self, new_target_map):
		self.target_map = new_target_map

	def run(self):
		self.running = True

		while(self.running):
			try:
				for log_entry in self.data_stream.log(skip_existing=True):
					if(log_entry.mod.name.lower() not in self.ignored_users[log_entry.subreddit.lower()]):
						log_subreddit_name = None
						try:
							log_subreddit_name = self.target_map[log_entry.subreddit.lower()]
						except KeyError:
							print("Log Subreddit Not Found for {0}".format(log_entry.subreddit.lower()))

						if(log_subreddit_name != None):
							log_subreddit = self.reddit.subreddit(log_subreddit_name)

							output = []
							if(log_entry.target_author):
								output+=["Target User: u/{0}".format(log_entry.target_author)]

							if(log_entry.action == 'banuser'):
								output+=["Duration: {0}".format(log_entry.details)]
								output+=["Reason: {0}".format(log_entry.description)]

							if(log_entry.target_permalink):
								output+=["URL: {0}".format(log_entry.target_permalink)]

							if(log_entry.target_title):
								output+=["Title: {0}".format(log_entry.target_title)]

							if(log_entry.target_body):
								output+=["Body:\n\n{0}".format(log_entry.target_body)]

							log_subreddit.submit(
								#validate_on_submit=True,
								title="{0} performed action `{1}`".format(log_entry.mod, log_entry.action),
								selftext="" if len(output) == 0 else "\n\n".join(output)
							)
			except KeyboardInterrupt:
				self.kill()
			except Exception as e:
				traceback.print_exc()
