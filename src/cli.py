from src.cAST_frontend import compress
from src.constants import Mode, Output
from src import __version__


def cli():
    """Cli implementation"""
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, max_help_position=35, width=100
        )
    )
    parser.add_argument(
        "-D",
        "--dataset",
        dest='dataset',
        default=False,
        help="Analyse data-set by it's path.",
    )
    parser.add_argument(
        "-f",
        "--file",
        dest='file',
        help="Source code path that will be analysed",
        type=argparse.FileType('r', encoding='UTF-8'),
    )
    parser.add_argument(
        "-m",
        "--mode",
        dest='mode',
        default=Mode.EXEC,
        choices=Mode.get_attr(),
        help="Compiler mode (choices: %(choices)s) (default: %(default)s)",
    )
    parser.add_argument(
        "-O",
        "--output-type",
        dest='output_type',
        default=Output.Format.JSON,
        choices=Output.Format.get_attr(),
        help="output type (choices: %(choices)s) (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        dest='output_file',
        default=Output.Location.SYSTEM_OUT,
        help="Write in output file (example: ~/path/to/file) (default: %(default)s)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--with-report",
        dest='with_report',
        help="Output comparison analysis between original AST and custom AST.",
        action="store_true"
    )
    args = parser.parse_args()
    if args.output_type == Output.Format.PICKLE and args.output_file is Output.Location.SYSTEM_OUT:
        parser.error("Chosen PICKLE output but no -o/--output-file specified.")
    if args.output_type == Output.Format.PICKLE and args.report:
        parser.error("PICKLE and report combination not available. Please, choose JSON format to extract report.")
    compress(
        file=args.file.read(),
        filename=args.file.name,
        mode=args.mode,
        output_type=args.output_type,
        output_file=args.output_file,
        report=args.with_report,
        dataset_path=args.dataset
    )
