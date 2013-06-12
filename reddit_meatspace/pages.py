import random

from pylons import c, g
from pylons.i18n import _
from babel.dates import format_date

from r2.lib.pages import Templated, BoringPage, WrappedUser
from r2.lib.template_helpers import format_number
from r2.lib.utils import Storage

from reddit_meatspace import utils
from reddit_meatspace.conversation_starters import TOPICS


class MeatspacePage(BoringPage):
    extra_stylesheets = BoringPage.extra_stylesheets + ["meatspace.less"]
    extra_page_classes = ["meatspace-page"]

    def __init__(self, **kwargs):
        BoringPage.__init__(self,
            pagename=_("reddit meetups"),
            show_sidebar=False,
            **kwargs
        )


class MeetupPortal(Templated):
    def __init__(self, meetup):
        self.meetup = meetup

        self.date = meetup.date.date()
        self.date_text = format_date(self.date, "long", locale=c.locale)

        self.find_meetup_url = self.date.strftime("http://redditgifts.com/"
                                                  "meetups/%m/%d/%Y")

        self.show_finder = meetup.state in ("prep", "active")
        self.show_badge = meetup.state in ("prep", "active")
        self.show_connect = meetup.state in ("active", "after")
        self.show_connections = meetup.state in ("after", "closed")

        Templated.__init__(self)


class LoggedOutMeetupPortal(MeetupPortal):
    pass


class ClosedMeetupPortal(MeetupPortal):
    pass


class MeatspaceBadgePage(MeatspacePage):
    extra_page_classes = MeatspacePage.extra_page_classes + ["badge-page"]


class ConversationStarterSelector(Templated):
    def __init__(self, meetup, user):
        self.meetup = meetup
        self.topics = []

        for topic, generator in TOPICS.iteritems():
            self.topics.append({
                "code": topic,
                "title": generator.title(),
                "content": generator(user),
            })

        Templated.__init__(self)


class QrCodeBadge(Templated):
    def __init__(self, meetup, user, topic):
        self.meetup = meetup
        self.username = user.name
        self.link_karma = format_number(max(user.karma("link"), 0))
        self.comment_karma = format_number(max(user.karma("comment"), 0))
        self.registration_date = format_date(user._date, "medium", c.locale)

        self.code = "%02d" % utils.make_secret_code(meetup, user)
        self.url = "%s/or/%s/%s" % (g.shortdomain, user.name, self.code)

        if not topic:
            topic = random.choice(TOPICS.keys())
        starter = TOPICS[topic]
        self.starter = Storage(
            title=starter.title(),
            content=starter(user),
        )

        Templated.__init__(self)


class MobileQrCodeBadge(QrCodeBadge):
    def __init__(self, meetup, user):
        QrCodeBadge.__init__(self, meetup, user, topic=None)


class QrCodeConnections(Templated):
    def __init__(self, meetup, connections):
        self.meetup = meetup

        self.connections = []
        for account in connections:
            wrapped = WrappedUser(account)
            wrapped.is_friend = account._id in c.user.friends
            self.connections.append(wrapped)
        self.my_fullname = c.user._fullname

        Templated.__init__(self)


class QrCodeForm(Templated):
    pass
