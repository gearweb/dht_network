import pykka
import random
from typing import List
import time
from logger import DataCapture
from utils import all_node_ids, node_ref
from node import Node, Discover, NodeAttributes
import uuid

def create_nodes(nodes_count:int, bootstrap_count:int):
    logger_ref = DataCapture.start()
    i = 0
    while i < nodes_count:
        id = 0
        while True: # to prevent duplicate id's been created
            id = random.randint(1, nodes_count*4)
            # id = int(uuid.uuid4())
            if id not in all_node_ids():
                break
        peers = all_node_ids()[0:bootstrap_count] # use the first few nodes as the bootstrap nodes
        Node.start(logger=logger_ref, id=id, peers=peers, peers_count=bootstrap_count)
        node_ref(id).tell(Discover(node=id)) # start the discovery phase for the new node
        i = i + 1
        # time.sleep(0.8)

if __name__== "__main__":
    create_nodes(nodes_count=200, bootstrap_count=2) 

    # all_nodes = pykka.ActorRegistry.get_all()
    for i in range(0,0):
        time.sleep(0.8)
        # print("all_nodes: " + str(len(all_nodes)) + " node_registry.keys() " + str(len(node_registry.keys())))
        for id in all_node_ids():
            peers = node_ref(id).ask(NodeAttributes.Peers)
            node_ref(id).tell(Discover(node=id)) # start the discovery phase for the new node

    time.sleep(0.8)
    for id in all_node_ids():
        s_id = str(node_ref(id).ask(NodeAttributes.Id))
        s_peers = str(node_ref(id).ask(NodeAttributes.Peers))
        distance = [id^p for p in node_ref(id).ask(NodeAttributes.Peers)]
        print("id: " + s_id + ", peers: " + s_peers) # + ", xor_distance: "+str(distance))

    # pykka.ActorRegistry.stop_all()
