import datetime

from pycassa import types
from pylons import g

from r2.lib.db import tdb_cassandra
from r2.models import Account


class Meetup(tdb_cassandra.Thing):
    _use_db = True
    _timestamp_prop = None
    _defaults = {
        # one of:
        # - "prep": finding meetups and printing badges
        # - "active": badges and connections
        # - "after": just connections
        # - "closed": all done
        "state": "prep",
    }
    _extra_schema_creation_args = dict(
        key_validation_class=types.AsciiType(),
        default_validation_class=types.UTF8Type(),
        column_validation_classes={
            "date": types.DateType(),
        },
    )
    _read_consistency_level = tdb_cassandra.CL.ONE
    _write_consistency_level = tdb_cassandra.CL.ALL
    _date_props = (
        "date",
    )

    @classmethod
    def _new(cls, codename, title, meetup_date):
        meetup = cls(
            _id=codename,
            title=title,
            date=meetup_date,
            body="",
        )
        meetup._commit()
        return meetup


class MeetupConnections(tdb_cassandra.View):
    _use_db = True
    _value_type = "date"
    _read_consistency_level = tdb_cassandra.CL.QUORUM
    _write_consistency_level = tdb_cassandra.CL.QUORUM
    _extra_schema_creation_args = dict(
        key_validation_class=types.AsciiType(),
        default_validation_class=types.DateType(),
    )

    @classmethod
    def _connect(cls, meetup, user, other):
        now = datetime.datetime.now(g.tz)
        values = {":".join((user._id36, other._id36)): now}
        cls._set_values(meetup._id, values)


class MeetupConnectionsByAccount(tdb_cassandra.View):
    _use_db = True
    _value_type = "str"
    _read_consistency_level = tdb_cassandra.CL.QUORUM
    _write_consistency_level = tdb_cassandra.CL.QUORUM
    _extra_schema_creation_args = dict(
        key_validation_class=types.AsciiType(),
        default_validation_class=types.AsciiType(),
    )

    @staticmethod
    def _rowkey(meetup, user):
        return ":".join((meetup._id, user._id36))

    @classmethod
    def _connect(cls, meetup, user, other):
        rowkey = cls._rowkey(meetup, user)
        cls._set_values(rowkey, {other._id36: ""})

    @classmethod
    def _connections(cls, meetup, user):
        rowkey = cls._rowkey(meetup, user)
        connections = cls.get_time_sorted_columns(rowkey).keys()
        return Account._byID36(connections, return_dict=False, data=True)
