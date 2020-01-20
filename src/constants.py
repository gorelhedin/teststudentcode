class Output:
    """Type of outputted AST representation enabled"""
    class Format:
        JSON = "json"
        PICKLE = "pickle"

        @staticmethod
        def get_attr() -> list:
            """Getter of Output class attributes"""
            return [Output.Format.JSON, Output.Format.PICKLE]

    class Location:
        SYSTEM_OUT = "system_out"

        @staticmethod
        def get_attr() -> list:
            """Getter of Output class attributes"""
            return [Output.Location.SYSTEM_OUT]


class Mode:
    """The mode argument specifies what kind of code must be compiled;
    it can be:
        'exec':      if source consists of a sequence of statements
        'eval':      if it consists of a single expression
        'single':    if it consists of a single interactive statement
                        (expression statements that evaluate to something
                        other than None will be printed).
    """
    EXEC = "exec"
    EVAL = "eval"
    SINGLE = "single"

    @staticmethod
    def get_attr() -> list:
        """Getter of Mode class attributes"""
        return [Mode.EXEC, Mode.EVAL, Mode.SINGLE]


class Logger:
    """Logger used constants"""
    NAME = "cAST.log"


class Origin:
    """Class to gather origin related constants"""
    SYSTEM = 'SYS'
    NATIVE = 'NATIVE'
    USER = 'USR'
    UNKNOWN = 'UNK'

    class Buildin_Functions:
        """List of in-build functions by python3.8.1"""
        INBUILD = ['abs', 'all', 'any', 'ascii', 'bin', 'bool', 'breakpoint', 'bytearray', 'bytes', 'callable', 'chr',
                   'classmethod', 'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec',
                   'filter', 'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex', 'id',
                   'input', 'int', 'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max', 'memoryview',
                   'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'print', 'property', 'range', 'repr', 'reversed',
                   'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
                   'vars', 'zip', '__import__']