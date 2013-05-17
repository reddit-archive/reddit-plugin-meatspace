from pylons.i18n import N_

from r2.lib.plugin import Plugin
from r2.config.routing import not_in_sr
from r2.lib.js import Module


class Meatspace(Plugin):
    needs_static_build = True

    js = {
        "meatspace-qrcode": Module("meatspace-qrcode.js",
            "lib/jquery.qrcode.min.js",
            "meatspace-qrcode.js",
        ),
    }

    errors = {
        "MEETUP_NOT_WITH_SELF": N_("you can't connect with yourself"),
        "MEETUP_INVALID_CODE": N_("that is not the correct code"),
    }

    def add_routes(self, mc):
        mc("/meetup/:codename/:action", controller="qrcode", action="portal",
           conditions={"function": not_in_sr})

        mc("/api/meetup_connect", controller="qrcode", action="connect",
           conditions={"function": not_in_sr})

        # shortdomain stuff is handled in haproxy, but haproxy can only prefix
        # paths that come through during rewrite. we'll handle it from there.
        mc("/meetup/:codename/or/:user/:code", controller="qrcode",
           action="connect_shortlink", conditions={"function": not_in_sr})

    def load_controllers(self):
        from reddit_meatspace.qrcode import QrCodeController
