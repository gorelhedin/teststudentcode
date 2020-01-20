import unittest
from src.cAST_frontend import compress
from src.constants import Mode, Output


class TestCAST(unittest.TestCase):
    def test_customiseAST_empty_file(self):
        """When report asked from an empty file, assert output is only one module node in top.

        :return:
        """
        file_path = 'tests/test_empty.py'
        file = open(file_path, 'r')
        eval = compress(
            file=file.read(),
            filename=file_path,
            mode=Mode.EXEC,
            output_type=Output.Format.JSON,
            output_file=None,
            report=True,
            dataset_path=None
        )
        file.close()
        true_eval = {'ast':
                         {'total_entities': 1,
                          'total_nodes': 1,
                          'entities': ['Module']},
                     'cast':
                         {'total_entities': 1,
                          'total_nodes': 1,
                          'entities': ['Module']}
                     }
        assert(eval == true_eval)

    def test_customiseAST_test_file(self):
        """When report asked, check that it retrieves a dict object.

        :return:
        """
        file_path = 'tests/test_file.py'
        file = open(file_path, 'r')
        eval = compress(
            file=file.read(),
            filename=file_path,
            mode=Mode.EXEC,
            output_type=Output.Format.JSON,
            output_file=None,
            report=True,
            dataset_path=None
        )
        file.close()
        assert(isinstance(eval, dict))

    def test_compression(self):
        """Check if some kind of compression was achieved when feeding test_file.py.

        :return:
        """
        file_path = 'tests/test_file.py'
        file = open(file_path, 'r')
        eval = compress(
            file=file.read(),
            filename=file_path,
            mode=Mode.EXEC,
            output_type=Output.Format.JSON,
            output_file=None,
            report=True,
            dataset_path=None
        )
        file.close()
        ast_entities_eval = eval.get('ast').get('total_entities')
        ast_nodes_eval = eval.get('ast').get('total_nodes')

        cast_entities_eval = eval.get('cast').get('total_entities')
        cast_nodes_eval = eval.get('cast').get('total_nodes')

        assert cast_nodes_eval < ast_nodes_eval
        assert cast_entities_eval < ast_entities_eval


if __name__ == '__main__':
    unittest.main()
