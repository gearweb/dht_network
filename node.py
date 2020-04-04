import pykka
from typing import List, Callable
from collections import namedtuple
import utils 
import enum
import logger
from logger import EventCreateNode, EventPeersUpdated 
from random import sample 
from collections import OrderedDict

Discover = namedtuple('Discover', ['node'])
Announce = namedtuple('Announce', ['peers'])

class NodeAttributes(enum.Enum):
   Id = 1
   Peers = 2

class Node(pykka.ThreadingActor):
    def __init__(self, logger:pykka.ActorRef, id:int, peers:List[int]=[], peers_count:int=1):
        super().__init__()
        self.logger:pykka.ActorRef = logger
        self.id:int = id 
        self.peers_count:int = peers_count
        self.peers:List[int] = peers

        # log create event
        self.logger.tell(EventCreateNode(node=self.id, peers=self.peers, distance=[p^self.id for p in peers]))

    def __setattr__(self, name, value):
        if name == 'peers': # when state change, log it
            rand_sample = []
            if len(value[self.peers_count:len(value)]) >= self.peers_count:
                rand_sample = sample(value[self.peers_count:len(value)], self.peers_count) 
            peers =value[0:self.peers_count] + rand_sample
            # peers =value
            self.logger.tell(EventPeersUpdated(node=self.id, peers=peers, distance=[p^self.id for p in peers]))
        super().__setattr__(name, value)
        
    def on_receive(self, message):
        if isinstance(message, Announce):
            self.announce(message.peers)
            print(str(message.peers) + " " +str(self.id)+" " +str(self.peers))
        if isinstance(message, NodeAttributes):
            if message==NodeAttributes.Id:
                return self.id
            if message==NodeAttributes.Peers:
                return self.peers
        if isinstance(message, Discover):
            self.discovery(message.node)
        return None

    def discovery(self, j_node:int):
        if j_node in self.peers:
            return
        # print("discovery id: " + str(self.id) + " j_node: " + str(j_node))
        self.append_peers([j_node]) # add joining node to this nodes peers
        peers = self.peers.copy() # list contains joining node

        # if joining node is this node, sent discovery to this joining nodes neerby peers.
        if self.id == j_node:
            # peer list will not contain self.id
            close_peers = distance_sort(peers, j_node)[0:self.peers_count]
            self.peers = [] # remove bootstrap nodes from this peer
            for peer in close_peers :
                utils.node_ref(peer).tell(Discover(node=j_node))
            return

        # remove joining node, will only work now with this nodes peers
        if j_node in peers:
            peers.remove(j_node)
        if len(peers) == 0: # if no peer exist, return
            return

        close_peers = distance_sort(peers, j_node)[0:self.peers_count]
        # close_peers = sample(distance_sort(peers, j_node)[0:self.peers_count*2], self.peers_count)
        # if the closets neighbor is this node, stop with discovery and announce it to the joining node
        # distance_jnode_self_id = j_node^self.id
        # distance_closets_peer = close_peers[0]^self.id
        # if j_node in close_peers:
        #     utils.node_ref(j_node).tell(Announce(peers=close_peers))
        #     return

        # else, send the joining node to this nodes closets peers with discovery
        for peer in close_peers:
            utils.node_ref(peer).tell(Discover(node=j_node))

        return 

    def announce(self, nodes:List[int]):
        # this is called from nodes that has recieved this node's id with discovery
        self.append_peers(nodes)

    def append_peers(self, peers):
        for peer in peers:
            if peer not in self.peers and peer != self.id:
                self.peers.append(peer)
        self.peers = distance_sort(self.peers, self.id)

def diff(list1, list2): 
    return list(set(list1) - set(list2))

def distance_sort(nodes:List[int], node:int) -> List[int]:
    if nodes == [] or nodes == None:
        return []
    xor_sorted = sort_func(vlist=nodes, value=node, sorting_func=distance_xor_diff)
    dif_sorted = sort_func(vlist=nodes, value=node, sorting_func=distance_diff)
    combined = xor_sorted + dif_sorted
    combined[::2] = xor_sorted
    combined[1::2] = dif_sorted
    combined = list(OrderedDict.fromkeys(combined))
    nodes.sort()
    return xor_sorted

def sort_func(vlist:List[int], value:int, sorting_func: Callable[[List[int], int], List[int]]) -> List[int]:
    distanceList = sorting_func(vlist, value)
    distances, sorted_list = (list(t) for t in zip(*sorted(zip(distanceList, vlist))))
    return sorted_list

def distance_xor_diff(vlist:List[int], value:int) -> List[int]:
    # return [abs(v^value-value) for v in vlist]
     return [v^value for v in vlist]

def distance_diff(vlist:List[int], value:int) -> List[int]:
    return [abs(v-value) for v in vlist]
