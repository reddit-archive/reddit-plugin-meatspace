from pylons.controllers.util import abort

from r2.lib.db import tdb_cassandra
from r2.lib.validator import Validator

from reddit_meatspace import models, conversation_starters


class VMeetup(Validator):
    def run(self, codename):
        if codename:
            try:
                return models.Meetup._byID(codename)
            except tdb_cassandra.NotFound:
                pass
        abort(404)


class VConversationStarter(Validator):
    def run(self, topic):
        if topic and topic in conversation_starters.TOPICS:
            return topic
        return None
