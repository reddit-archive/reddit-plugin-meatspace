#!/usr/bin/python

from __future__ import print_function, division

import networkx

from reddit_meatspace.models import MeetupConnections


connections = MeetupConnections._byID("2013")
digraph = networkx.DiGraph()
for connection, timestamp in connections._values().iteritems():
    left, right = connection.split(":")
    digraph.add_edge(left, right)

lenient = digraph.to_undirected(reciprocal=False)
strict = digraph.to_undirected(reciprocal=True)
meetups = networkx.connected_component_subgraphs(lenient)

print("{0} people @ {1} meetups (avg. {2:.2} per meetup)".format(
    len(lenient), len(meetups), len(lenient) / len(meetups)))
print("{0} connections of {1} distinct meetings ({2:.2%})".format(strict.size(), lenient.size(), strict.size() / lenient.size()))
