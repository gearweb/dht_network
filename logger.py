from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from functools import partial
import pykka
import random
import json
from collections import namedtuple
import enum

EventCreateNode = namedtuple('EventCreateNode', ['node', 'peers', 'distance'])
EventPeersUpdated = namedtuple('EventCreateNode', ['node', 'peers', 'distance'])

class GetEvents(enum.Enum):
   Nodes = 1
   Peers = 2

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, logger:pykka.ActorRef, *args, **kwargs):
        self.logger:pykka.ActorRef = logger
        # BaseHTTPRequestHandler calls do_GET **inside** __init__ !!!
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path=="/nodes_created":
            nodes = [{'id': event.node , 'label': str(event.node)} for event in self.logger.ask(GetEvents.Nodes)]
            # edge = {'from': rnd, 'to': rnd2}
            body = json.dumps(nodes)
            print(body)
            self.create_json_response(nodes)

        if self.path=="/edges_updated":
            edges = {}
            event_dict = self.logger.ask(GetEvents.Peers)
            for node_id in event_dict.keys():
                # edges[node_id] = [{'id': str(node_id) + '-' + str(peer), 'from': node_id, 'to': peer, 'length': distance} for peer, distance in zip(event_dict[node_id].peers, event_dict[node_id].distance)]
                edges[node_id] = [{'id': str(node_id) + '-' + str(peer), 'from': node_id, 'to': peer} for peer, distance in zip(event_dict[node_id].peers, event_dict[node_id].distance)]
 
            body = json.dumps(edges)
            print(body)
            self.create_json_response(edges)

    def create_json_response(self, body):
            s_body = json.dumps(body) # convert to string
            self.send_response(200)
            self.send_header("Content-Length", str(len(s_body))) 
            self.send_header('Content-Type', 'application/json')
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(s_body.encode()) # convert to bytes

def create_server(logger:pykka.ActorRef):
    handler = partial(HTTPRequestHandler, logger)
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, handler)
    httpd.serve_forever()

class DataCapture(pykka.ThreadingActor): # used to log events from Nodes 
    def __init__(self ):
        super().__init__()
        # start the http server so that data can now be access from a outside process
        self.processThread = threading.Thread(target=create_server, args=(self.actor_ref,), daemon=True) # daemon: thread will die on program termination
        self.processThread.start()

        # events, changes that happen
        self.events_node_created = []
        self.events_peers_updated = {}

    def on_receive(self, message):
        if isinstance(message, EventCreateNode):
            self.events_node_created.append(message)
            print("logger EventCreateNode: " + str(message.node) + " peers" + str(message.peers))
        if isinstance(message, EventPeersUpdated):
            self.events_peers_updated[message.node] = message
        if isinstance(message, GetEvents):
            # when data is fetched, clear current events
            if message==GetEvents.Nodes:
                events_create_node = self.events_node_created.copy()
                self.events_node_created = []
                return events_create_node
            if message==GetEvents.Peers:
                events_peers_updated = self.events_peers_updated.copy()
                self.events_peers_updated = {}
                return events_peers_updated
        return
