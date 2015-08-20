import hashlib

from pylons import app_globals as g


def make_secret_code(meetup, user):
    hash = hashlib.md5(g.secrets["SECRET"])
    hash.update(str(meetup._id))
    hash.update(str(user._id))
    return int(hash.hexdigest()[-8:], 16) % 100
