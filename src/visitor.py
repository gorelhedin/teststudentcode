from src.logger import get_logger
import ast
import src.cAST as cAST

logger = get_logger('Visitor')


class Visitor(ast.NodeVisitor):
    """Visitor class to traverse ast
    While traversing existing ast, a custom AST (cAST) is persisted.
    cAST takes in to account imports in code and their aliases in order to homogenise the ast.
    """
    def __init__(self, inbuild_imports, sys_imports):
        self.custom_ast = None
        self.inbuild_imports = inbuild_imports
        self.sys_imports = sys_imports
        self.aliases = dict()

    def set_custom_ast(self, cast):
        self.custom_ast = cast

    def get_custom_ast(self) -> cAST:
        return self.custom_ast

    def save_alias(self, alias: str, original: str):
        self.aliases.update({alias: original})

    # =============================================================================================
    # Utils Visitor
    # =============================================================================================

    @staticmethod
    def _format(node: ast) -> dict:
        """Get a dict representation of node.

        :param node: Node to format
        :return: dict representation of node
        """
        # If ast.AST, get all fields under such node and their pair value.
        if isinstance(node, ast.AST):
            args = []
            keywords=False
            for field in node._fields:
                try:
                    value = getattr(node, field)
                except AttributeError:
                    keywords = True
                else:
                    if keywords:
                        args.append({field: Visitor._format(value)})
                    else:
                        args.append(Visitor._format(value))
            return {node.__class__.__name__: args}
        # If list, create a list of formatted childs and return it
        elif isinstance(node, list):
            return [Visitor._format(x) for x in node]
        # Arrived to this point, should provide representation of primitive types like str, float, etc.
        return repr(node)

    def alias2original(self, alias: str) -> str:
        """Given an alias, search it in available ones and provide original name.
        If not found, return same name.

        :param alias: key string to look in self.aliases
        :return: linked name for alias
        """
        if alias in self.aliases:
            return self.aliases.get(alias)
        return alias

    @staticmethod
    def get_generic_attributes(node: ast.AST) -> dict:
        """By default, attributes stored in cAST will be a list of the values retrieved
        by Visitor._format().

        :param node: ast.AST node to extract attributes
        :return: dict
        """
        return Visitor._format(node).values()

    @staticmethod
    def initialise_child(parent: cAST.Node, child: ast):
        """Create cAST node given child ast node. Set child's parent. Set child as parent's child.

        :param parent: parent ast node
        :param child: child ast node
        :return:
        """
        cast_child = cAST.Node(child)
        cast_child.set_parent(parent)
        parent.set_child(cast_child)

    # END Utils Visitor
    # ---------------------------------------------------------------------------------------------

    # =============================================================================================
    # Generic TRAVERSE OF ast.AST
    # =============================================================================================

    def generic_visit(self, node, general_behaviour=True, look_down=True):
        """Shared/Generic behaviour when visiting node.

        :param node: ast.AST Node being traversed
        :param general_behaviour: bool. apply general behaviour or not
        :param look_down: keep recursive traversal after this node
        :return:
        """
        metadata = self._format(node)
        if isinstance(node, ast.Module):
            node_module = cAST.Node(node)
            node_module.set_metadata(metadata)
            self.populate_CAST_node(node_module)
            cast_module = cAST.cAST(root=node_module)
            self.set_custom_ast(cast_module)
        elif isinstance(node, ast.AST):
            cast_node = self.get_custom_ast().find_node(node)
            cast_node.set_metadata(metadata)
            if general_behaviour:
                cast_node.set_is_default_attributes(general_behaviour)
                self.populate_CAST_node(cast_node)
        else:
            logger.error('expected ast.AST or ast.Module, got %r' % node.__class__.__name__)
        if look_down:
            ast.NodeVisitor.generic_visit(self, node)

    @staticmethod
    def populate_CAST_node(node: cAST):
        """Given a CAST node, create subsequent CAST childs and link them to node.
        If no child found, that node is a leaf node. Get attributes and set_attributes().
        If childs found, that node is a parent node. Initialise childs.

        :param node: cAST node to populate
        :return:
        """
        ast_node = node.get_ast_node()
        iterator = ast.iter_child_nodes(ast_node)
        try:
            first_child = next(iterator)
            Visitor.initialise_child(parent=node, child=first_child)
        except StopIteration:
            attributes = Visitor.get_generic_attributes(ast_node)
            node.set_attributes(attributes)
        for child in iterator:
            Visitor.initialise_child(parent=node, child=child)

    # END Generic TRAVERSE OF ast.AST
    # ---------------------------------------------------------------------------------------------

    # =============================================================================================
    # CUSTOM visit for ast.AST node
    # =============================================================================================

    def _treat_import(self, node):
        from src.constants import Origin
        attributes = list()
        for alias in node.names:
            if alias.asname is not None:
                self.save_alias(alias=alias.asname, original=alias.name)
            if alias.name in self.inbuild_imports:
                attributes.append({"origin": Origin.NATIVE})
            elif alias.name in self.sys_imports:
                attributes.append({"origin": Origin.SYSTEM})
            else:
                attributes.append({"origin": Origin.UNKNOWN})
            if isinstance(node, ast.ImportFrom):
                attributes.append({"name": node.module + "." + alias.name})
            elif isinstance(node, ast.Import):
                attributes.append({"name": alias.name})
            else:
                raise("Non accepted class in Import treatment.")
        return attributes

    def visit_Import(self, node):
        cast_node = self.get_custom_ast().find_node(node)
        attributes = self._treat_import(node)
        cast_node.set_is_default_attributes(False)
        cast_node.set_attributes(attributes)
        self.generic_visit(node, general_behaviour=False, look_down=False)

    def visit_ImportFrom(self, node):
        cast_node = self.get_custom_ast().find_node(node)
        attributes = self._treat_import(node)
        cast_node.set_is_default_attributes(False)
        cast_node.set_attributes(attributes)
        self.generic_visit(node, general_behaviour=False, look_down=False)

    @staticmethod
    def _treat_name(node) -> list:
        attributes = list()
        formatted_node = Visitor._format(node)
        name_values = list(formatted_node.values())[0]  # format: [[id, {action: [args]}]]
        id = name_values[0]
        action_dict = name_values[1]
        action = list(action_dict.keys())[0]
        attributes.append({"id": id, "ctx": action})
        return attributes

    def visit_NameConstant(self, node):
        self.generic_visit(node)

    def visit_Name(self, node):
        cast_node = self.get_custom_ast().find_node(node)
        attributes = self._treat_name(node)
        cast_node.set_is_default_attributes(False)
        cast_node.set_attributes(attributes)
        self.generic_visit(node, general_behaviour=False, look_down=False)

    def _treat_call(self, node: ast) -> list:
        from src.constants import Origin
        attributes = list()
        func_call = node.__dict__.get('func')
        original_id = self.alias2original(func_call.__dict__.get('id'))
        if original_id in self.sys_imports:
            attributes.append({'origin': Origin.SYSTEM})
        elif original_id in self.inbuild_imports:
            attributes.append({'origin': Origin.NATIVE})
        else:
            attributes.append({'origin': Origin.UNKNOWN})
        change_id = {'id': original_id}
        func_call.__dict__.update(change_id)
        return attributes

    def visit_Call(self, node):
        cast_node = self.get_custom_ast().find_node(node)
        attributes = self._treat_call(node)
        cast_node.set_is_default_attributes(False)
        cast_node.set_attributes(attributes)
        self.populate_CAST_node(cast_node)
        self.generic_visit(node, general_behaviour=False, look_down=True)

    @staticmethod
    def _treat_keyword(node: ast) -> list:
        attributes = list()
        arg = node.__dict__.get('arg')
        attributes.append({'arg': arg})
        return attributes

    def visit_keyword(self, node):
        cast_node = self.get_custom_ast().find_node(node)
        attributes = self._treat_keyword(node)
        cast_node.set_is_default_attributes(False)
        cast_node.set_attributes(attributes)
        self.populate_CAST_node(cast_node)
        self.generic_visit(node, general_behaviour=False, look_down=True)

    @staticmethod
    def _treat_attribute(node: ast) -> list:
        attributes = list()
        attr = node.__dict__.get('attr')
        attributes.append({'attr': attr})
        return attributes

    def visit_Attribute(self, node):
        cast_node = self.get_custom_ast().find_node(node)
        attributes = self._treat_attribute(node)
        cast_node.set_is_default_attributes(False)
        cast_node.set_attributes(attributes)
        self.populate_CAST_node(cast_node)
        self.generic_visit(node, general_behaviour=False, look_down=True)

    # END CUSTOM visit for ast.AST node
    # ---------------------------------------------------------------------------------------------

    # =============================================================================================
    # DEFAULT visit for ast.AST node
    # =============================================================================================

    def visit_Num(self, node):
        self.generic_visit(node)

    def visit_Str(self, node):
        self.generic_visit(node)

    def visit_FormattedValue(self, node):
        self.generic_visit(node)

    def visit_JoinedStr(self, node):
        self.generic_visit(node)

    def visit_Bytes(self, node):
        self.generic_visit(node)

    def visit_List(self, node):
        self.generic_visit(node)

    def visit_Tuple(self, node):
        self.generic_visit(node)

    def visit_Set(self, node):
        self.generic_visit(node)

    def visit_Dict(self, node):
        self.generic_visit(node)

    def visit_Ellipsis(self, node):
        self.generic_visit(node)

    def visit_Load(self, node):
        self.generic_visit(node)

    def visit_Store(self, node):
        self.generic_visit(node)

    def visit_Del(self, node):
        self.generic_visit(node)

    def visit_Starred(self, node):
        self.generic_visit(node)

    def visit_Expr(self, node):
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        self.generic_visit(node)

    def visit_UAdd(self, node):
        self.generic_visit(node)

    def visit_USub(self, node):
        self.generic_visit(node)

    def visit_Not(self, node):
        self.generic_visit(node)

    def visit_Invert(self, node):
        self.generic_visit(node)

    def visit_BinOp(self, node):
        self.generic_visit(node)

    def visit_Add(self, node):
        self.generic_visit(node)

    def visit_Sub(self, node):
        self.generic_visit(node)

    def visit_Mult(self, node):
        self.generic_visit(node)

    def visit_Div(self, node):
        self.generic_visit(node)

    def visit_FloorDiv(self, node):
        self.generic_visit(node)

    def visit_Mod(self, node):
        self.generic_visit(node)

    def visit_Pow(self, node):
        self.generic_visit(node)

    def visit_LShift(self, node):
        self.generic_visit(node)

    def visit_RShift(self, node):
        self.generic_visit(node)

    def visit_BitOr(self, node):
        self.generic_visit(node)

    def visit_BitXor(self, node):
        self.generic_visit(node)

    def visit_BitAnd(self, node):
        self.generic_visit(node)

    def visit_MatMult(self, node):
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.generic_visit(node)

    def visit_And(self, node):
        self.generic_visit(node)

    def visit_Or(self, node):
        self.generic_visit(node)

    def visit_Compare(self, node):
        self.generic_visit(node)

    def visit_Eq(self, node):
        self.generic_visit(node)

    def visit_NotEq(self, node):
        self.generic_visit(node)

    def visit_Lt(self, node):
        self.generic_visit(node)

    def visit_LtE(self, node):
        self.generic_visit(node)

    def visit_Gt(self, node):
        self.generic_visit(node)

    def visit_GtE(self, node):
        self.generic_visit(node)

    def visit_Is(self, node):
        self.generic_visit(node)

    def visit_IsNot(self, node):
        self.generic_visit(node)

    def visit_In(self, node):
        self.generic_visit(node)

    def visit_NotIn(self, node):
        self.generic_visit(node)

    def visit_IfExp(self, node):
        self.generic_visit(node)

    def visit_Subscript(self, node):
        self.generic_visit(node)

    def visit_Index(self, node):
        self.generic_visit(node)

    def visit_Slice(self, node):
        self.generic_visit(node)

    def visit_ExtSlice(self, node):
        self.generic_visit(node)

    def visit_ListComp(self, node):
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.generic_visit(node)

    def visit_comprehension(self, node):
        self.generic_visit(node)

    def visit_Assign(self, node):
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self.generic_visit(node)

    def visit_Print(self, node):
        self.generic_visit(node)

    def visit_Raise(self, node):
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.generic_visit(node)

    def visit_Delete(self, node):
        self.generic_visit(node)

    def visit_Pass(self, node):
        self.generic_visit(node)

    def visit_alias(self, node):
        self.generic_visit(node)

    def visit_If(self, node):
        self.generic_visit(node)

    def visit_For(self, node):
        self.generic_visit(node)

    def visit_While(self, node):
        self.generic_visit(node)

    def visit_Break(self, node):
        self.generic_visit(node)

    def visit_Continue(self, node):
        self.generic_visit(node)

    def visit_Try(self, node):
        self.generic_visit(node)

    def visit_TryFinally(self, node):
        self.generic_visit(node)

    def visit_TryExcept(self, node):
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.generic_visit(node)

    def visit_With(self, node):
        self.generic_visit(node)

    def visit_withitem(self, node):
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.generic_visit(node)

    def visit_Lambda(self, node):
        self.generic_visit(node)

    def visit_arguments(self, node):
        self.generic_visit(node)

    def visit_arg(self, node):
        self.generic_visit(node)

    def visit_Return(self, node):
        self.generic_visit(node)

    def visit_Yield(self, node):
        self.generic_visit(node)

    def visit_YieldFrom(self, node):
        self.generic_visit(node)

    def visit_Global(self, node):
        self.generic_visit(node)

    def visit_Nonlocal(self, node):
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.generic_visit(node)

    def visit_Await(self, node):
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.generic_visit(node)

    def visit_AsyncWith(self, node):
        self.generic_visit(node)

    # END DEFAULT visit for ast.AST node
    # ---------------------------------------------------------------------------------------------