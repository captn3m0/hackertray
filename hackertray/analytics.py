from mixpanel import Mixpanel


class Analytics:
    # Setup analytics.
    # dnt - do not track. Disables tracking if True
    # token - The mixpanel token
    def __init__(self, dnt, token):
        self.dnt = dnt
        self.tracker = Mixpanel(token)
        if(self.dnt is True):
            print("[+] Analytics disabled")
    # Track an event
    # event - string containing the event name
    # data  - data related to the event, defaults to {}

    def track(self, event, data={}):
        if(self.dnt is False):
            # All events are tracked anonymously
            self.tracker.track("anonymous", event, data)
    # Track a visit to a URL
    # The url maybe an HN submission or
    # some meta-url pertaining to hackertray

    def visit(self, url):
        self.track('visit', {"link": url})
