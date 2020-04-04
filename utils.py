import pykka
from typing import List
from node import Node
import logger 

def all_node_ids() -> List[pykka.ActorRef]:
    return [n._actor.id for n in pykka.ActorRegistry.get_by_class(Node)]

def node_ref(id:int) -> pykka.ActorRef:
    for n_ref in pykka.ActorRegistry.get_by_class(Node):
       if n_ref._actor.id == id:
           return n_ref
    return None

def logger_ref() -> List[pykka.ActorRef]:
    loggers = pykka.ActorRegistry.get_by_class(logger.DataCapture)
    if len(loggers) == 0:
        return None

    return loggers[0]
