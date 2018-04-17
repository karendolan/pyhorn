#!/usr/bin/env python

"""
Outputs the hours of content of Matterhorn events. See --help for options.


Holding off on partial work. Using the other example as model

Outputs:
Per week & per Month: the number of 
1. The number of new events
2. The number of repubs
3. The duration of new events
4. The total duration of new event source (presenter & presenation)
5. The total duration of delievered media for new events
6. The total duration of delivered media for repubs

Approach: 
1. Loop through a few months of archived events starting from today
2. Put events into MHEvent data structure
2.1 is_repub => mediapckage.metadata.catalog.[{type="republish/origin"}]
2.2 id => mediapackage.id
2.3 date_start => mediapckage.start
2.5 source_duration_source => get first mediapackage.media.track[{type:"*/source", duration:xyz}] 
2.5 source_count => loop count mediapackage.media.track[{type:"*/source"}] 
2.6 delivery_duration => get first mediapackage.media.track[{type:"*/delivery", duration:xyz}]
2.6 deliver_count => loop mediapackage.media.track[{type:"*/delivery"}]
3. loop through MHEvents to count totals for outputs

For week stufff, started referencing
ref: https://gist.github.com/bradmontgomery/5110985

e.g., ./episode_hour_count.py -u foo -p bar http://matterhorn.example.edu
"""

from pyhorn import MHClient
from argparse import ArgumentParser

def main(args):

    mh = MHClient(args.host, args.username, args.password)
    increment_current = 0
    increment_offset = 10 #this should always match the limit, or you'll process dups
    increment_max = 50
    if args.limit is not None:
        increment_max = args.limit
    max_events = increment_max * increment_offset;

    # LOOP

    # get a set of archives from the current offset, most resent to historical
    increment_episodes = mh.episodes(offset=(current_offset*offset_increment), limit=increment_offset, sort="DATE_CREATED_DESC")

 ...
    print len(counts)

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('host', help='Opencast or Matterhorn host (including scheme)')
    parser.add_argument('-u','--username', help='Matterhorn system user')
    parser.add_argument('-p','--password', help='Matterhorn system user password')
    parser.add_argument('-l','--limit', action='append',
                        help="The maximum number of events to consider, starting from today",
                        default='500')

    args = parser.parse_args()
    main(args)

# Data structure for event
class MHEvent(object):

    def __init__(self, mp_id, is_repub=False, date_started, source_dur, source_count, delivery_dur, delivery_count):
        self.mp_id = mp_id
        self.is_repub = is_repub
        self.date_started = date_started
        self.source_dur = source_dur
        self.source_count = source_count
        self.delivery_dur = delivery_dur
        self.deliver_count = delivery_count
