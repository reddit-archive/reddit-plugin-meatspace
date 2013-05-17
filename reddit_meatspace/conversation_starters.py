from pylons.i18n import _, N_

from r2.models import Subreddit


TOPICS = {}


def conversation_starter(title):
    def conversation_starter_decorator(fn):
        TOPICS[fn.__name__] = fn
        fn.title = lambda: _(title)
        return fn
    return conversation_starter_decorator


@conversation_starter(N_("april fools' team"))
def f2p_team(user):
    return "orangered" if user._id % 2 == 0 else "periwinkle"


@conversation_starter(N_("most active in"))
def top_sr(user):
    all_karmas = user.all_karmas()
    if not all_karmas:
        return _("lurker")
    top_sr = all_karmas[0]
    return "/r/" + top_sr[0]


_ZODIAC_SIGNS = [
    N_("capricorn"),
    N_("aquarius"),
    N_("pisces"),
    N_("aries"),
    N_("taurus"),
    N_("gemini"),
    N_("cancer"),
    N_("leo"),
    N_("virgo"),
    N_("libra"),
    N_("scorpio"),
    N_("sagittarius"),
]


@conversation_starter(N_("snoo-o-logical sign"))
def zodiac(user):
    return _(_ZODIAC_SIGNS[user._date.month % 12])


@conversation_starter(N_("most obscure"))
def obscure(user):
    all_karmas = user.all_karmas()
    if not all_karmas:
        return _("lurker")
    srnames = [x[0] for x in all_karmas]
    srs = [sr for sr in Subreddit._by_name(srnames).values()
           if sr.type in ("public", "restricted")]
    if not srs:
        return _("something secret")
    srs.sort(key=lambda sr: sr._downs)
    most_obscure = srs[0]
    return "/r/" + most_obscure.name
