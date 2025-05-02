import time
from bitsets import bitset
from collections import defaultdict
import pybgpstream
import gzip
import configparser


config = configparser.ConfigParser()
config.read('config/config.ini')


#bitset configs:
MAX_DIRECT_PEERS = 3000
highest_peer_id_used = 0
peer_to_id = {}
id_to_peer = {}
peer_id_list = range(MAX_DIRECT_PEERS)
direct_peer_set = bitset("peers", tuple(peer_id_list))


class DirectPeerSet:

        def __init__(self):
                self.peer_bitset = direct_peer_set()

        def add_peer(self, peer_string):
                global highest_peer_id_used
                global peer_to_id
                global id_to_peer
                global direct_peer_set
                try:
                        new_peer_id = peer_to_id[peer_string]
                except:
                        if highest_peer_id_used >= MAX_DIRECT_PEERS:
                                print("increase max direct peers")
                                raise

                        peer_to_id[peer_string] = highest_peer_id_used
                        id_to_peer[highest_peer_id_used] = peer_string
                        new_peer_id = peer_to_id[peer_string]
                        highest_peer_id_used += 1

                self.peer_bitset = self.peer_bitset.union(direct_peer_set((new_peer_id,)))

        def get_peers(self):
                peer_ids = list(self.peer_bitset)
                #print str(sys.getsizeof(self.peer_bitset))
                return [id_to_peer[x] for x in peer_ids] #map(id_to_peer,peer_ids)


def get_collector_list():
        with open(config['path']['collector_list_path'], 'r') as f:
                return [collector.replace('\n', '') for collector in f.readlines()]


def get_bgpstream(collector_name, start, end, record_type='ribs'):
        '''Returns the started BGPStream and the BGPRecord of recordType('rib' or 'update') created filtering by collector_name and TS (timestamp) interval'''
        stream = pybgpstream.BGPStream(
                from_time=start, until_time=end,
                collector=collector_name,
                record_type=record_type,
                filter='elemtype announcements' if record_type == 'updates' else None)
        return stream


def process_stream(stream, collector, origin_dp, transit_dp, start_time):
        record_count = 0
        for rec in stream.records():
                # if rec.dump_position != previous_dump_pos:
                #       logging.info("dump time: %s, rec time: %s, dump_pos:%s", rec.dump_time, rec.time, rec.dump_position)
                #       previous_dump_pos = rec.dump_position
                for elem in rec:
                        as_path = elem.fields['as-path']
                        if '{' not in as_path and '(' not in as_path and len(as_path) > 0:
                                # good path (no set, no confederation, no empty path)
                                dp_key = str(elem.peer_asn) + ':' + collector
                                path = as_path.split(' ')
                                # origin = path[-1]
                                origin = path.pop()
                                pfx = elem.fields["prefix"]
                                if ':' not in pfx and 8 <= int(pfx.split('/')[1]) <= 24:
                                        # IPv4 /8-/24
                                        origin_dp[origin].add_peer(dp_key)
                                        for asn in set(path):
                                                transit_dp[asn].add_peer(dp_key)
                                elif ':' in pfx and 8 <= int(pfx.split('/')[1]) <= 64:
                                        # IPv6 /8-/64
                                        origin_dp[origin].add_peer(dp_key)
                                        for asn in set(path):
                                                transit_dp[asn].add_peer(dp_key)
                        record_count += 1
                        if record_count % 1000000 == 0:
                                print('{} records {} time: {}'.format(collector, record_count, (time.time() - start_time)))
        print('{} {} records number: {} time: {}'.format(collector, start_time, record_count, (time.time() - start_time)))

        return record_count


def download(record_type='ribs', start="2020-01-01 07:30:00", end="2020-01-01 08:30:00"):
        global log
        #log = get_logger(str(os.path.basename(__file__).split('.')[0]) + '_' + record_type, record_type)
        print('start date: {} end date : {}'.format(start, end))

        date = start.split(' ')[0]
        start_time = time.time()
        origin_dp = defaultdict(DirectPeerSet)
        transit_dp = defaultdict(DirectPeerSet)
        record_count_total = 0
        collector_list = get_collector_list()
        #collector_list = ['rrc00', 'route-views2']
        #collector_list = ['route-views.amsix']
        #collector_list = ['rrc00']

        for i, collector in enumerate(collector_list):
                print(collector)
                stream = get_bgpstream(collector, start, end, record_type)
                record_count_total += process_stream(stream, collector, origin_dp, transit_dp, start_time)
                print('{}/{} completed'.format(i + 1, len(collector_list)))
        print('all collectors records {} origin asn {}  transit asn {} time: {}'.format(record_count_total, len(origin_dp), len(transit_dp), (time.time() - start_time)))

        template = config['path']['raw_file_path'] + config['constant']['raw_file_template']
        write_results_to_file(origin_dp, template.format(date, record_type, 'origin'))
        write_results_to_file(transit_dp, template.format(date, record_type, 'transit'))
        del origin_dp
        del transit_dp


def write_results_to_file(dp_list, output_file):
        with gzip.open(output_file, 'wt') as outfile:
                outfile.write('ASN|dp_count|dp_list\n')
                for asn in dp_list:
                        dps = set([dp_col.split(':')[0] for dp_col in dp_list[asn].get_peers()])
                        outfile.write(asn + '|' + str(len(dps)) + '|' + ','.join(dps) + '\n')
