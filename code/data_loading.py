import json
import node
import time_personalized 


def loadNodes(doc):
    nodes = []
    with open(doc) as f:
        data = json.load(f)
        for key, value in data["nodes"].items():
            nodes.append(node.node(key, time_personalized.getTimeFromData(value["Data"]), value["Dependencies"]))
    return nodes
