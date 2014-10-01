from mixpanel import Mixpanel

class Analytics:
    # Setup analytics.
    # dnt - do not track. Disables tracking if True
    # token - The mixpanel token
    @staticmethod
    def setup(dnt, token):
        Analytics.dnt = dnt
        Analytics.tracker = Mixpanel(token)
        if(dnt == True):
            print "[+] Analytics disabled"
    # Track an event
    # event - string containing the event name
    # data  - data related to the event, defaults to {}
    @staticmethod
    def track(event, data = {}):
        if(Analytics.dnt == False):
            # All events are tracked anonymously
            Analytics.tracker.track("anonymous", event, data)
    # Track a visit to a URL
    # The url maybe an HN submission or 
    # some meta-url pertaining to hackertray
    @staticmethod
    def visit(url):
        Analytics.track('visit', url)