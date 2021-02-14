from collections import defaultdict
import traceback

class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret

class InviteAcceptor():
    def __init__(self, reddit, target_subs={}, log_sub_suffixes=["_modlog", "_log", "__modlog", "__log"], sub_created_cb=None):
        self.reddit = reddit
        self.inbox = reddit.inbox.stream(skip_existing=True)
        self.log_sub_suffixes = log_sub_suffixes
        self.sub_created_cb = sub_created_cb
        self.target_subs = keydefaultdict(self.create_log_subreddit, target_subs)

    def kill(self):
        self.running = False

    def create_log_subreddit(self, source_sub):
        #Attempt to Register Log-Sub
        target_sub = None
        for suffix in self.log_sub_suffixes:
            log_subreddit_name = "{0}{1}".format(source_sub, suffix)
            target_sub = self.reddit.subreddit.create(
                name=log_subreddit_name,
                title="Public Modlog for {0}".format(source_sub)
            )
            if(target_sub != None):
                break

        if(self.sub_created_cb != None and target_sub != None):
            self.sub_created_cb(source_sub, log_subreddit_name)

        return target_sub.display_name

    def run(self):
        self.running = True
        while(self.running):
            try:
                for message in self.inbox:
                    if(message.subreddit and
                        message.subject.startswith('invitation to moderate /r/') and
                        message.body.startswith('gadzooks!')):
                        message.subreddit.mod.accept_invite()
                        log_sub = self.target_subs[message.subreddit.display_name.lower()]
                        if(log_sub != None):
                            message.reply("You have added /u/{0}, a Modlog Transparency Bot to your mod team.\n\nFuture mod actions will be posted to /r/{1}".format(self.reddit.user.me().name, log_sub))
                        else:
                            message.reploy("You have added /u/{0}, a Modlog Transparency Bot to your mod team.\n\nI couldn't make a log-sub for you just yet. I've let my creator know.".format(self.reddit.user.me().name))
                            print("COULD NOT MAKE A MODLOG SUB FOR /r/{0}".format(message.subreddit.display_name))
            except KeyboardInterrupt as e:
                self.running = False
            except Exception as e:
                traceback.print_exc()
