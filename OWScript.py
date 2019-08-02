import argparse
import os
import re
import sys
import time
from OWScript import Errors
from OWScript.Errors import Logger
from OWScript.Lexer import Lexer
from OWScript.Parser import Parser
from OWScript.Transpiler import Transpiler

def transpile(text, path, args):
    """Transpiles an OWScript code into Overwatch Workshop rules."""
    start = time.time()
    Errors.TEXT = text
    lexer = Lexer(text=text + '\n')
    tokens = lexer.lex()
    if args.tokens:
        if args.save:
            with open(args.save, 'w', errors='ignore') as f:
                f.write(lexer.print_tokens())
        else:
            lexer.print_tokens()
    parser = Parser(tokens=tokens)
    tree = parser.script()
    if args.tree:
        print(tree.string())
    logger = Logger(log_level=args.debug)
    transpiler = Transpiler(tree=tree, path=path, logger=logger)
    code = transpiler.run()
    if args.min:
        code = re.sub(r'[\s\n]*', '', code)
    if not args.save:
        if sys.stdout.encoding.strip() != 'utf-8':
            sys.stderr.write(
                f'[WARNING] Python encoding output set to {sys.stdout.encoding} (not utf-8), '
                'unicode characters on the output will be interpreted as ascii. '
                'Consider using `set PYTHONIOENCODING=utf_8` and running the command again.'
            )
        sys.stdout.write(code)
    else:
        try:
            with open(args.save, 'wb') as f:
                code = code.encode('utf-8')
                f.write(code)
        except FileNotFoundError:
            raise Errors.FileNotFoundError('Output directory not found.')
            sys.exit(Errors.ExitCode.OutputNotFound)
    if args.copy:
        import pyperclip
        pyperclip.copy(code)
        sys.stdout.write('\nCode copied to clipboard.')
    end = time.time()
    if args.time:
        print('\nTime Elapsed: {}s'.format(round(end - start, 2)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Overwatch Workshop code from OWScript')
    parser.add_argument('input', nargs='*', type=str, help='Standard input to process')
    parser.add_argument('-m', '--min', action='store_true', help='Minifies the output by removing whitespace')
    parser.add_argument('-s', '--save', help='Save the output to a file instead of printing it')
    parser.add_argument('-c', '--copy', action='store_true', help='Copies output to clipboard automatically')
    parser.add_argument('-t', '--time', action='store_true', help='Debug: outputs the time elapsed to generate the output')
    parser.add_argument('-d', '--debug', type=int, default=Logger.WARN, help='The severity level of the logger (1=Info, 2=Warning, 3=Debug)')
    parser.add_argument('--tokens', action='store_true', help='Debug: shows the tokens created by the lexer')
    parser.add_argument('--tree', action='store_true', help='Debug: visualizes the AST generated by the parser')
    args = parser.parse_args()
    if args.input:
        file_input = args.input[0]
        path = os.path.abspath(file_input)
        try:
            with open(path, 'rb') as f:
                text = f.read().decode('utf-8')
        except FileNotFoundError:
            raise Errors.FileNotFoundError('Input file not found.')
            sys.exit(Errors.ExitCode.InputNotFound)
    else:
        text = sys.stdin.read()
        path = os.getcwd()
    try:
        transpile(text, path=path, args=args)
    except Errors.OWSError as ex:
        sys.stderr.write('Error: {}'.format(ex))
        sys.exit(Errors.ExitCode.CompileError)