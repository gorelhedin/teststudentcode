from ast import *
from src.constants import Output, Mode
from src.eval import analyse
from src.logger import get_logger
from src.visitor import Visitor


logger = get_logger('cAST-frontend')


def compress(file: str, filename: str, mode: str, output_type: str, output_file: str, report: bool, dataset_path: str):
    if dataset_path:
        __analyse_dataset(dataset_path)
        return
    import ast2json
    import json
    inbuild_imp, sys_imp = get_imports(filename, '/python\d\.\d/')
    logger.debug("Found following potential in-build imports: '{}'".format(inbuild_imp))
    logger.debug("Found following potential sys imports: '{}'".format(sys_imp))
    visitor = Visitor(inbuild_imports=inbuild_imp, sys_imports=sys_imp)
    tree: AST = parse(file, filename=filename, mode=mode)
    my_file = open(filename)
    original_ast = json.dumps(ast2json.str2json(my_file.read()))
    my_file.close()
    logger.debug("Original ast ast='{}'".format(original_ast))
    visitor.visit(tree)
    c_ast = visitor.get_custom_ast()
    if output_type == Output.Format.JSON:
        custom_ast = c_ast.jsonify(output_file)
    elif output_type == Output.Format.PICKLE:
        c_ast.pickleify(output_file)
    if report:
        evaluation = analyse(original_ast, custom_ast)
        logger.debug(evaluation)
        return evaluation


def get_imports(file_path: str, to_match: str) -> list:
    import modulefinder
    import re
    from src.constants import Origin
    sys = list()
    native = Origin.Buildin_Functions.INBUILD
    modfind = modulefinder.ModuleFinder()
    modfind.run_script(file_path)
    pattern = re.compile(to_match)
    for k, v in modfind.modules.items():
        if pattern.search(str(v.__file__)):
            sys.append(k)
    return native, sys


def __analyse_dataset(path_dataset):
    import os
    import matplotlib.pyplot as plt

    names = list()
    dataset_ast_nodes = [0]
    dataset_cast_nodes = [0]
    dataset_ast_entities = [0]
    dataset_cast_entities = [0]
    pos = 0
    for filename in os.listdir(path_dataset):
        if filename.endswith(".py"):
            pos += 1
            file_path = path_dataset + filename
            file = open(file_path, 'r').read()
            try:
                eval = compress(
                    file=file,
                    filename=file_path,
                    mode=Mode.EXEC,
                    output_type=Output.Format.JSON,
                    output_file=None,
                    report=True,
                    dataset_path=None
                )
                names.append(file_path)
                eval_ast = eval.get('ast')
                eval_cast = eval.get('cast')

                dataset_ast_entities.append(dataset_ast_entities[-1] + eval_ast.get('total_entities'))
                dataset_cast_entities.append(dataset_cast_entities[-1] + eval_cast.get('total_entities'))
                dataset_ast_nodes.append(dataset_ast_nodes[-1] + eval_ast.get('total_nodes'))
                dataset_cast_nodes.append(dataset_cast_nodes[-1] + eval_cast.get('total_nodes'))

                if len(names) == 10000:
                    plt.plot(dataset_ast_nodes, label='AST')
                    plt.plot(dataset_cast_nodes, label='custom AST')
                    plt.legend()
                    plt.ylabel("Number of nodes visited in data-set")
                    plt.xlabel("Number of files analysed")
                    plt.title("Nodes shown in data-set and analysed\n by DeepCode")
                    plt.show()
                    plt.plot(dataset_ast_entities, label='AST')
                    plt.plot(dataset_cast_entities, label='custom AST')
                    plt.legend()
                    plt.ylabel("Number of entities visited in data-set")
                    plt.xlabel("Total of files analysed")
                    plt.title("Entities shown in data-set and analysed\n by DeepCode")
                    plt.show()
            except Exception as e:
                logger.debug(e)
                pass
        else:
            continue
