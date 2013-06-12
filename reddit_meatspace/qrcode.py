import urllib

from pylons import c, g
from pylons.controllers.util import redirect_to

from r2.controllers import add_controller
from r2.controllers.reddit_base import RedditController
from r2.lib.validator import (
    validate,
    validatedForm,
    VExistingUname,
    VInt,
    VUser,
)
from r2.lib.errors import errors

from reddit_meatspace import pages, validators, models, utils


BADGE_STATES = {"prep", "active"}
CONNECT_STATES = {"active", "after"}


@add_controller
class QrCodeController(RedditController):
    @validate(
        meetup=validators.VMeetup("codename"),
    )
    def GET_portal(self, meetup):
        if meetup.state != "closed":
            if c.user_is_loggedin:
                content = pages.MeetupPortal(meetup=meetup)
            else:
                content = pages.LoggedOutMeetupPortal(meetup=meetup)
        else:
            content = pages.ClosedMeetupPortal(meetup=meetup)

        return pages.MeatspacePage(
            content=content,
            page_classes=["meatspace-portal"]
        ).render()

    @validate(
        VUser(),
        meetup=validators.VMeetup("codename"),
    )
    def GET_configure_badge(self, meetup):
        if meetup.state not in BADGE_STATES:
            return redirect_to("/meetup/%s" % str(meetup._id))

        content = pages.ConversationStarterSelector(meetup, c.user)
        return pages.MeatspacePage(content=content).render()

    @validate(
        VUser(),
        meetup=validators.VMeetup("codename"),
        topic=validators.VConversationStarter("topic"),
    )
    def GET_badge(self, meetup, topic):
        if meetup.state not in BADGE_STATES:
            return redirect_to("/meetup/%s" % str(meetup._id))

        content = pages.QrCodeBadge(meetup, c.user, topic)
        return pages.MeatspaceBadgePage(content=content).render()

    @validate(
        VUser(),
        meetup=validators.VMeetup("codename"),
    )
    def GET_mobile_badge(self, meetup):
        if meetup.state not in BADGE_STATES:
            return redirect_to("/meetup/%s" % str(meetup._id))

        content = pages.MobileQrCodeBadge(meetup, c.user)
        return content.render()

    @validate(
        VUser(),
        meetup=validators.VMeetup("codename"),
        other=VExistingUname("user"),
        connected_with=VExistingUname("connected-with"),
        code=VInt("code"),
    )
    def GET_connect(self, meetup, other, code, connected_with):
        if meetup.state not in CONNECT_STATES:
            self.abort404()

        content = pages.QrCodeForm(
            meetup=meetup,
            other=other,
            code=code,
            connected_with=connected_with,
        )
        return pages.MeatspacePage(content=content).render()

    @validatedForm(
        VUser(),
        meetup=validators.VMeetup("codename"),
        other=VExistingUname("username"),
        code=VInt("code"),
    )
    def POST_connect(self, form, jquery, meetup, other, code):
        if meetup.state not in CONNECT_STATES:
            self.abort403()

        jquery("body .connection-success").hide()

        if form.has_errors("username",
                           errors.NO_USER,
                           errors.USER_DOESNT_EXIST):
            return

        if c.user == other:
            c.errors.add(errors.MEETUP_NOT_WITH_SELF, field="username")
            form.set_error(errors.MEETUP_NOT_WITH_SELF, "username")
            return

        expected_code = utils.make_secret_code(meetup, other)
        if code != expected_code:
            g.log.warning("%r just tried an invalid code on %r",
                          c.user.name, other.name)
            c.errors.add(errors.MEETUP_INVALID_CODE, field="code")
            form.set_error(errors.MEETUP_INVALID_CODE, "code")
            return

        models.MeetupConnections._connect(meetup, c.user, other)
        models.MeetupConnectionsByAccount._connect(meetup, c.user, other)
        g.stats.simple_event("meetup.connection")

        form.redirect("/meetup/%s/connect?connected-with=%s" % (meetup._id,
                                                                other.name))

    @validate(
        VUser(),
        meetup=validators.VMeetup("codename"),
    )
    def GET_connections(self, meetup):
        all_connections = models.MeetupConnectionsByAccount._connections(
            meetup, c.user)
        connections = [a for a in all_connections if not a._deleted]

        content = pages.QrCodeConnections(
            meetup=meetup,
            connections=connections,
        )
        return pages.MeatspacePage(content=content).render()

    @validate(meetup=validators.VMeetup("codename"))
    def GET_connect_shortlink(self, meetup, user, code):
        if meetup.state not in CONNECT_STATES:
            self.abort404()

        params = urllib.urlencode({
            "user": user,
            "code": code,
        })
        return redirect_to("/meetup/%s/connect?%s" % (str(meetup._id), params),
                           _code=301)
