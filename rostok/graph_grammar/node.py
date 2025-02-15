from dataclasses import dataclass
from typing import Optional

import networkx as nx
from networkx.algorithms.traversal import dfs_preorder_nodes

from rostok.block_builder_api.block_blueprints import ALL_BLUEPRINT


@dataclass
class Node:
    """Contains information about the label and :py:class:`BlockBlueprint`,
    which is the physical representation of the node in the simulator
    """
    label: str = "*"
    is_terminal: bool = False

    # None for non-terminal nodes
    block_blueprint: Optional[ALL_BLUEPRINT] = None

    def __hash__(self) -> int:
        return hash(str(self.label) + str(self.is_terminal))

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            raise Exception(
                "Wrong type of comparable object. Must be Node instead {wrong_type}".format(
                    wrong_type=type(__o)))
        return self.label == __o.label


class Rule:
    """ The class contains a graph object for substitution into the generated graph
    and the target node which will be replaced by :py:attr:`Rule.graph_insert`.
    The feature of the rule's terminality is automatically determined.
    Id's mean V from graph theory, do not intersect with V from generated graph.
    """
    _graph_insert: nx.DiGraph = nx.DiGraph()
    replaced_node: Node = Node()
    # In local is system!
    id_node_connect_child = -1
    id_node_connect_parent = -1
    _is_terminal: bool = None

    @property
    def graph_insert(self):
        return self._graph_insert

    @graph_insert.setter
    def graph_insert(self, graph: nx.DiGraph):
        self._is_terminal = all(
            [raw_node["Node"].is_terminal for _, raw_node in graph.nodes(data=True)])
        self._graph_insert = graph

    @property
    def is_terminal(self):
        return self._is_terminal

    def __hash__(self):
        return hash(str(self.graph_insert) + str(self.replaced_node))


@dataclass
class UniqueBlueprint:
    """ The return type is used to build the Robot.
        Id - from the generated graph
    """
    id: int
    block_blueprint: ALL_BLUEPRINT  # Set default value


ROOT = Node("ROOT")


class GraphGrammar(nx.DiGraph):
    """ A class for using generative rules (similar to L grammar) and
        manipulating the construction graph.
        The mechanism for assignment a unique Id, each added node using :py:meth:`GraphGrammar.rule_apply`
        will increase the counter.
        Supports methods from :py:class:`networkx.DiGraph` ancestor class
    """

    def __init__(self, **attr):
        super().__init__(**attr)
        self.__uniq_id_counter = -1
        self.add_node(self.get_uniq_id(), Node=ROOT)

    def get_uniq_id(self):
        self.__uniq_id_counter += 1
        return self.__uniq_id_counter

    def find_nodes(self, match: Node) -> list[int]:
        """

        Args:
            match (Node): Node for find, matched by label

        Returns:
            list[int]: Id of matched nodes
        """

        match_nodes = []
        for raw_node in self.nodes.items():
            # Extract node info
            node: Node = raw_node[1]["Node"]
            node_id = raw_node[0]
            if node.label == match.label:
                match_nodes.append(node_id)
        return match_nodes

    def _replace_node(self, node_id: int, rule: Rule):
        """Applies rules to node_id

        Args:
            node_id (int):
            rule (Rule):
        """

        # Convert to list for mutable
        in_edges = [list(edge) for edge in self.in_edges(node_id)]
        out_edges = [list(edge) for edge in self.out_edges(node_id)]

        id_node_connect_child_graph = self.get_uniq_id()

        is_equal_id = rule.id_node_connect_parent != rule.id_node_connect_child
        id_node_connect_parent_graph = self.get_uniq_id(
        ) if is_equal_id else id_node_connect_child_graph

        relabel_in_rule = \
            {rule.id_node_connect_child: id_node_connect_child_graph,
            rule.id_node_connect_parent: id_node_connect_parent_graph}

        for raw_nodes in rule.graph_insert.nodes.items():
            raw_node_id = raw_nodes[0]
            if raw_node_id in relabel_in_rule.keys():
                continue
            relabel_in_rule[raw_node_id] = self.get_uniq_id()

        for edge in in_edges:
            edge[1] = id_node_connect_parent_graph
        for edge in out_edges:
            edge[0] = id_node_connect_child_graph

        # Convert ids in rule to graph ids system
        rule_graph_relabeled = nx.relabel_nodes(rule.graph_insert, relabel_in_rule)

        # Push changes into graph
        self.remove_node(node_id)
        self.add_nodes_from(rule_graph_relabeled.nodes.items())
        self.add_edges_from(rule_graph_relabeled.edges)
        self.add_edges_from(in_edges)
        self.add_edges_from(out_edges)

    def closest_node_to_root(self, list_ids: list[int]) -> int:
        """Find closest node to root from list_ids

        Args:
            list_ids (list[int]):

        Returns:
            int: id of closest Node
        """

        root_id = self.get_root_id()

        def sort_by_root_path(node_id):
            paths = self.get_sorted_root_based_paths()
            for path in paths:
                if node_id in path:
                    return paths.index(path)
            return None

        def sort_by_root_distance(node_id):
            return len(nx.shortest_path(self, root_id, node_id))

        # after two sorts the nodes are sorted by distance to root and nodes
        # at the same distance are sorted by paths according to sorted root paths
        sorta = sorted(list_ids, key=sort_by_root_path)
        sorta = sorted(sorta, key=sort_by_root_distance)
        return sorta[0]

    def get_root_id(self) -> int:
        """

        Returns:
            int: root id
        """

        for raw_node in self.nodes.items():
            raw_node_id = raw_node[0]
            if self.in_degree(raw_node_id) == 0:
                root_id = raw_node_id
        return root_id

    def apply_rule(self, rule: Rule):
        ids = self.find_nodes(rule.replaced_node)
        edge_list = list(self.edges)
        id_closest = self.closest_node_to_root(ids)
        if rule.graph_insert.order() == 0:
            # Stub removing leaf node if input rule is empty
            out_edges_ids_node = list(filter(lambda x: x[0] == id_closest, edge_list))
            if out_edges_ids_node:
                raise Exception("Trying delete not leaf node")
            self.remove_node(id_closest)
        else:
            self._replace_node(id_closest, rule)

    def node_levels_bfs(self) -> list[list[int]]:
        """Divide nodes into levels.

        Return a list of lists of nodes where each inner list is a
        level in respect to the \'root\', which is the node with no in edges.
        This function should be reviewed once we start to use graphs with cycles and not just trees
        """
        levels = []
        # Get the root node that has no in_edges. Currently, we assume
        # that where is only one node without in_edges
        for raw_node in self.nodes.items():
            raw_node_id = raw_node[0]
            if self.in_degree(raw_node_id) == 0:
                root_id = raw_node_id

        current_level = [root_id]
        next_level = []
        # The list of edges that is built on the bases of the range to the source
        bfs_edges_list = list(nx.bfs_edges(self, source=root_id))
        for edge in bfs_edges_list:
            # If the edge starts in current level, the end of the edge appends to the next level
            if edge[0] in current_level:
                next_level.append(edge[1])
            # Else, the current level is finished and appended to the levels. next_level becomes
            # current_level and the end of the edge goes to the new  next_level
            else:
                levels.append(current_level)
                current_level = next_level
                next_level = [edge[1]]

        # Finish the levels by appending current and next_level. In the cycle the appending occurs,
        # when the edge of the next level is found.
        levels.append(current_level)
        levels.append(next_level)
        return levels

    def graph_partition_dfs(self) -> list[list[int]]:
        """ 2D list
            Row is branch of graph
            Collum is id node

        Returns:
            list[list[int]]:
        """

        paths = []
        path = []

        root_id = self.get_root_id()
        dfs_edges = nx.dfs_edges(self, root_id)
        dfs_edges_list = list(dfs_edges)

        for edge in dfs_edges_list:
            if len(self.out_edges(edge[1])) == 0:
                path.append(edge[1])
                paths.append(path.copy())
                path = []
            else:
                if len(path) == 0:
                    path.append(edge[0])
                    path.append(edge[1])
                else:
                    path.append(edge[1])
        return paths

    def build_unique_blueprint_array(self) -> list[list[UniqueBlueprint]]:
        """Returns a 2-d array of paths from root to each leaf

        Raises:
            Exception: Graph contain non-terminal elements

        Returns:
            list[list[WrapperTuple]]:
        """

        #paths = self.graph_partition_dfs()
        paths = self.get_root_based_paths()
        wrapper_array = []

        for path in paths:
            wrapper = []
            for node_id in path:
                node: Node = self.get_node_by_id(node_id)
                if node.is_terminal and node.block_blueprint:
                    buf = UniqueBlueprint(node_id, node.block_blueprint)
                    wrapper.append(buf)
                else:
                    raise Exception('Graph contain non-terminal elements')
            wrapper_array.append(wrapper.copy())

        return wrapper_array

    def get_root_based_paths(self):
        """Form the paths of node ids from root to each leaf
        
        Raises:
            Exception: the number of paths reached the limit

        Returns:
            list[list[int]]: list of paths, each path is a list of node ids
        """
        root_id = self.get_root_id()
        paths = [[root_id]]
        final_paths = []
        counter = 0
        while len(paths) > 0:
            if counter > 1000:
                raise Exception("Reached the iteration limit in number of paths in a graph")
            counter += 1
            new_paths = []
            for path in paths:
                end_id_path = path[-1]
                # neighbors in digraph returns list of children nodes
                children = list(self.neighbors(end_id_path))
                if len(children) == 0:
                    # no children <==> end of a path
                    final_paths.append(path)
                    continue
                else:
                    for child in children:
                        new_paths.append(path + [child])

            paths = new_paths

        return final_paths

    def get_node_by_id(self, node_id: int) -> Node:
        return self.nodes[node_id]["Node"]

    def get_ids_in_dfs_order(self) -> list[int]:
        """Iterate in deep first order over node ids
        One of the options to present the graph in a flat form

        Returns:
            list[int]:
        """

        return list(dfs_preorder_nodes(self, self.get_root_id()))

    def __eq__(self, __rhs) -> bool:
        if isinstance(__rhs, GraphGrammar):
            self_dfs_paths_lbl = self.get_uniq_representation()
            rhs_dfs_paths_lbl = __rhs.get_uniq_representation()
            return self_dfs_paths_lbl == rhs_dfs_paths_lbl
        return False

    def get_sorted_root_based_paths(self):
        """Sort root based paths by length and same lengths lexicographically."""
        root_based_paths = self.get_root_based_paths()

        def primary_key(path):
            return len(path)

        def secondary_key(path):
            string_path = [self.get_node_by_id(x).label for x in path]
            return "".join(string_path)

        root_based_paths.sort(key=secondary_key)
        root_based_paths.sort(key=primary_key)
        return root_based_paths

    def get_uniq_representation(self) -> list[list[str]]:
        """Returns dfs partition node labels. 
        Where branches is sorted by lexicographic order

        Returns:
            list[list[str]]: dfs branches 
        """

        self_root_base_paths = self.get_root_based_paths()
        self_dfs_paths_lbl = []
        for path in self_root_base_paths:
            self_dfs_paths_lbl.append([self.get_node_by_id(x).label for x in path])

        self_dfs_paths_lbl.sort(key=lambda x: "".join(x))
        return self_dfs_paths_lbl

    def __hash__(self) -> int:
        self_dfs_paths_lbl = self.get_uniq_representation()
        return hash(str(self_dfs_paths_lbl))
