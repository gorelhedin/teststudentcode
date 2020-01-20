from src.logger import get_logger

logger = get_logger('evaluation')


def analyse(original_tree, custom_tree):
    import json
    original_tree_dict = json.loads(original_tree)
    node_appearances_AST = dict()
    iter_tree(original_tree_dict, node_appearances_AST, type_key="_type")
    num_entities_ast = len(list(node_appearances_AST.keys()))
    num_nodes_ast = sum(list(node_appearances_AST.values()))
    ast_analysis = {'total_entities': num_entities_ast,
                    'total_nodes': num_nodes_ast,
                    'entities': list(node_appearances_AST.keys())}

    custom_tree_dict = json.loads(custom_tree)
    node_appearances_cAST = dict()
    iter_tree(custom_tree_dict, node_appearances_cAST, type_key="CAST_type")
    num_entities_cast = len(list(node_appearances_cAST.keys()))
    num_nodes_cast = sum(list(node_appearances_cAST.values()))
    cast_analysis = {'total_entities': num_entities_cast,
                     'total_nodes': num_nodes_cast,
                     'entities': list(node_appearances_cAST.keys())}
    logger.debug("Analysis AST: Different entities '{}', Total nodes '{}'".format(num_entities_ast, num_nodes_ast))
    logger.debug("Analysis cAST: Different entities '{}', Total nodes '{}'".format(num_entities_cast, num_nodes_cast))
    return {'ast': ast_analysis, 'cast': cast_analysis}


def iter_tree(d, entities_tree, type_key):
    for k, v in d.items():
        if k == type_key:
            if v in entities_tree:
                curr_value = entities_tree.get(v)
                entities_tree.update({v: curr_value + 1})
            else:
                entities_tree.update({v: 1})
        if isinstance(v, dict):
            iter_tree(v, entities_tree, type_key)
        elif isinstance(v, list):
            [iter_tree(element, entities_tree, type_key) for element in v if isinstance(element, dict)]


if __name__ == "__main__":
    #D1={"CAST_type": "Module", "CAST_body": [{"CAST_type": "Import", "CAST_body": [{"origin": "SYS"}, {"name": "pprint"}]}, {"CAST_type": "Import", "CAST_body": [{"origin": "UNK"}, {"name": "src.my_pretty.my_print"}]}, {"CAST_type": "FunctionDef", "CAST_body": [{"CAST_type": "arguments", "CAST_body": [{"CAST_type": "arg", "CAST_body": ["'list1'", "None"]}]}, {"CAST_type": "Loop", "CAST_body": [{"CAST_type": "Name", "CAST_body": [{"id": "'i'", "ctx": "Store"}]}, {"CAST_type": "Name", "CAST_body": [{"id": "'list1'", "ctx": "Load"}]}, {"CAST_type": "Expr", "CAST_body": [{"CAST_type": "Call", "CAST_body": [{"origin": "SYS"}, {"CAST_type": "Name", "CAST_body": [{"id": "'pprint'", "ctx": "Load"}]}, {"CAST_type": "Call", "CAST_body": [{"origin": "UNK"}, {"CAST_type": "Name", "CAST_body": [{"id": "'my_print'", "ctx": "Load"}]}, {"CAST_type": "Name", "CAST_body": [{"id": "'i'", "ctx": "Load"}]}]}]}]}]}]}]}
    D1 = {"CAST_type": "Module","tests":{"inner":1}, "CAST_body": [{"CAST_type":"Name", "CAST_body": [{"origin": "SYS"}, {"name": "pprint"}]}]}
    node_appearances = {}
    iter_tree(D1, node_appearances)
    print(node_appearances)