import pandas as pd


class Node:
    def __init__(self, node_id, line):
        self.node_id = node_id
        self.line = line


class Edge:
    def __init__(self, starting_node_id, ending_node_id, distance, line):

        self.starting_node_id = starting_node_id
        self.ending_node_id = ending_node_id
        self.distance = distance
        self.line = line


def get_nodes(pd_frame):
    starting_nodes = pd_frame["from_stop_I"].tolist()
    ending_nodes = pd_frame["to_stop_I"].tolist()
    return set(starting_nodes + ending_nodes)


def add_node(pd_frame, node):
    for key in node.keys():
        pd_frame[key].append(node[key])
    return pd_frame


def add_edge(network, edge):
    network["from_stop_I"].append(edge.starting_node_id)
    network["to_stop_I"].append(edge.ending_node_id)
    network["d"].append(edge.distance)
    network["n_vehicles"].append(edge.line)

    return network


def is_edge_in_network(network, edge):

    common_sets = [i for i in range(0, len(network["from_stop_I"]))]

    common_sets = [i for i in common_sets if str(network["from_stop_I"][i]) == str(edge.starting_node_id)]
    common_sets = [i for i in common_sets if str(network["to_stop_I"][i]) == str(edge.ending_node_id)]
    common_sets = [i for i in common_sets if str(network["d"][i]) == str(edge.distance)]
    common_sets = [i for i in common_sets if str(network["n_vehicles"][i]) == str(edge.line)]

    return len(common_sets) != 0


def get_transfer_duration(pd_frame, line_in, line_out):

    input_lines = pd_frame.loc[pd_frame["n_vehicles_in"] == line_in]

    if len(input_lines) == 0:
        return 0

    selected_line = input_lines.loc[pd_frame["n_vehicles_out"] == line_out]

    if len(selected_line) == 0:
        return 0

    duration = selected_line["d"].tolist()
    assert len(duration) == 1
    duration = duration[0]

    return duration


def main():

    pd_frame = pd.read_csv("data/network.csv", delimiter=";")
    transfer_time_frame = pd.read_csv("data/transition_time.csv", delimiter=";")
    all_nodes = get_nodes(pd_frame)

    extended_network = {"from_stop_I": [],
                        "to_stop_I": [],
                        "d": [],
                        "n_vehicles": []}

    for node in all_nodes:

        incoming_nodes_idxs = pd_frame.loc[pd_frame["to_stop_I"] == node].index.tolist()
        outgoing_connections_idxs = pd_frame.loc[pd_frame["from_stop_I"] == node].index.tolist()

        new_in_nodes = []
        new_out_nodes = []
        for incoming_connections_idx in incoming_nodes_idxs:

            line = str(pd_frame.loc[incoming_connections_idx, "n_vehicles"])

            starting_node_id = str(pd_frame.loc[incoming_connections_idx, "from_stop_I"])
            ending_node_id = str(node)
            distance = pd_frame.loc[incoming_connections_idx, "d"]

            starting_node = Node(node_id=starting_node_id + "_" + line + "_out",
                                 line=line)

            ending_node = Node(node_id = ending_node_id + "_" + line + "_in",
                               line=line)

            if ending_node.node_id not in [item.node_id for item in new_in_nodes]:
                new_in_nodes.append(ending_node)

            edge = Edge(starting_node_id=starting_node.node_id,
                        ending_node_id=ending_node.node_id,
                        distance=distance,
                        line=line
                        )

            if not is_edge_in_network(extended_network, edge):
                add_edge(extended_network, edge)

        for outgoing_connections_idx in outgoing_connections_idxs:
            line = str(pd_frame.loc[outgoing_connections_idx, "n_vehicles"])
            distance = pd_frame.loc[outgoing_connections_idx, "d"]

            starting_node_id = str(node) + "_" + line + "_out"
            ending_node_id = str(pd_frame.loc[outgoing_connections_idx, "to_stop_I"]) + "_" + line + "_in"

            starting_node = Node(node_id=starting_node_id,
                                 line=line)

            ending_node = Node(node_id=ending_node_id,
                               line=line)

            if starting_node.node_id not in [item.node_id for item in new_out_nodes]:
                new_out_nodes.append(starting_node)

            edge = Edge(starting_node_id=starting_node.node_id,
                        ending_node_id=ending_node.node_id,
                        distance=distance,
                        line=line
                        )

            if not is_edge_in_network(extended_network, edge):
                add_edge(extended_network, edge)

        for node_in in new_in_nodes:
            for node_out in new_out_nodes:

                duration = get_transfer_duration(transfer_time_frame, line_in=node_in.line, line_out=node_out.line)

                edge = Edge(starting_node_id = node_in.node_id,
                            ending_node_id=node_out.node_id,
                            distance=duration,
                            line="transfer")

                if not is_edge_in_network(extended_network, edge):
                    add_edge(extended_network, edge)

    expanded_frame = pd.DataFrame(extended_network)
    expanded_frame.to_csv("data/expanded_network.csv")

if __name__ == '__main__':
    main()