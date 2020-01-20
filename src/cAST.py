import ast
from src.constants import Output
from src.logger import get_logger

logger = get_logger('customAST')


class Groups:
    """Grouping of ast.AST Node entities"""
    IMPORT_GROUP = "Import"
    LOOP_GROUP = "Loop"
    NAME_GROUP = "Name"

    @staticmethod
    def merge_by_group(ast_node):
        if isinstance(ast_node, ast.ImportFrom) or isinstance(ast_node, ast.Import):
            return Groups.IMPORT_GROUP
        elif isinstance(ast_node, ast.For) or isinstance(ast_node, ast.While):
            return Groups.LOOP_GROUP
        elif isinstance(ast_node, ast.Name) or isinstance(ast_node, ast.NameConstant):
            return Groups.NAME_GROUP
        return ast_node.__class__.__name__


class Node:
    """Node of custom AST.
    Each node contains:
        - self.ast_node: Link to it's ast.AST node
        - self.name: cAST name
        - self.is_default_attributes: attributes behaviour boolean
        - self.attributes: attributes information
        - self.metadata: extra information
        - self.parent: Node acting as it's parent
        - self.childs: list(Nodes) acting as it's childs
    """
    def __init__(self, ast_node):
        self.ast_node = ast_node
        self.name = Groups.merge_by_group(ast_node)
        self.is_default_attributes = None
        self.attributes = None
        self.metadata = None
        self.parent = None
        self.childs = list()

    def get_ast_node(self):
        return self.ast_node

    def set_parent(self, parent):
        self.parent = parent

    def get_parent(self):
        return self.parent

    def set_attributes(self, attributes):
        self.attributes = attributes

    def get_attributes(self):
        return self.attributes

    def set_metadata(self, metadata):
        self.metadata = metadata

    def get_metadata(self):
        return self.metadata

    def set_child(self, child):
        assert isinstance(child, Node)
        child.set_parent(self)
        self.childs.append(child)

    def set_is_default_attributes(self, is_default_attributes):
        self.is_default_attributes = is_default_attributes

    def get_is_default_attributes(self):
        return self.is_default_attributes

    def look_down(self, node):
        """Traverse downside cAST in order to find node.

        :param node: node to find
        :return: Node or None if not found
        """
        if node == self.ast_node:
            return self
        for child in self.childs:
            found = child.look_down(node)
            if isinstance(found, Node):
                return found
        return None

    def print_subtree(self, indentation=0):
        """Print representation of self down to all it's leafs."""
        print("-"*indentation + repr(self.ast_node))
        logger.debug("-"*indentation + repr(self.ast_node))
        for child in self.childs:
            child.print_subtree(indentation+4)

    def to_dict(self) -> dict:
        """Provide dict representation of self down to all it's leafs.

        :return: dict
        """
        node_as_list = list()
        if self.attributes:
            if self.is_default_attributes:
                body = list()
                [body.extend(attribute) for attribute in self.attributes]
                return {"CAST_type": self.name, "CAST_body": body}
            else:
                if isinstance(self.attributes, list):
                    node_as_list.extend(self.attributes)
                elif isinstance(self.attributes, dict):
                    node_as_list.append(self.attributes)
        if self.childs:
            node_childs = list()
            for child in self.childs:
                node_childs.append(child.to_dict())
            if node_childs:
                node_as_list.extend(node_childs)
        return {"CAST_type": self.name, "CAST_body": node_as_list}


class cAST:
    """custom AST (cAST) object"""
    def __init__(self, root):
        assert(isinstance(root, Node))
        self.root = root

    def find_node(self, node) -> Node:
        """Find node in cAST.

        :param node: Node to find
        :return: node or None if not found
        """
        return self.root.look_down(node)

    def print_tree(self):
        """Print full tree with Node representations"""
        self.root.print_subtree()

    def jsonify(self, file_name):
        """Build tree as json and retrieve it in demanded output.
        Possible outputs:
            - System Out
            - File

        :param file_name: File to output. Can be path or Output.Location.SYSTEM_OUT
        :return:
        """
        import json

        json_custom_ast = json.dumps(self.root.to_dict())
        logger.debug(json_custom_ast)
        if file_name is Output.Location.SYSTEM_OUT:
            print(json_custom_ast)
        elif file_name:
            file = open(file_name, 'w')
            json.dump(json_custom_ast, file)
            file.close()
        return json_custom_ast

    def pickleify(self, file_name):
        """Create cAST pickle and dump it in file.

        :param file_name: path to file pickle representation of cAST
        :return:
        """
        import pickle

        file = open(file_name, 'wb')
        pickle.dump(self, file)
        file.close()