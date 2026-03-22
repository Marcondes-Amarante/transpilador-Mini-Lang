from lexer import Lexer, LexicalError
from parser import Parser, MiniLangSyntaxError
from semantic import AnalisadorSemantico, SemanticError

from pathlib import Path
import sys

ARTIFACTS_FOLDER = Path("./artifacts")
file_name = "arquivo"


def main():
    global file_name

    args_list: list[str] = sys.argv
    if len(args_list) < 2:
        print("Uso: python main.py <codigo_fonte>.txt [-save] [-print]")
        return

    try:
        caminho: Path = Path(args_list[1])
        codigo_fonte: str = carregar_arquivo(caminho)
        file_name = caminho.stem

        save_flag = "-save" in args_list
        print_flag = "-print" in args_list

        if save_flag:
            ARTIFACTS_FOLDER.mkdir(parents=True, exist_ok=True)

        lexer: Lexer = lexer_analysis(codigo_fonte, save_flag, print_flag)
        parser: Parser = parser_analysis(lexer, save_flag, print_flag)


        print("\n>>> Sucesso: Código léxico, sintático e tipos validados!")
    except LexicalError as e:
        print(e)
    except MiniLangSyntaxError as e:
        print(e)
    except SemanticError as e:
        print(e)
    except Exception as e:
        print(f"Erro: {e}")


def lexer_analysis(
    code: str, save_flag=False, print_flag=False, file_name="arquivo"
) -> Lexer:
    lexer: Lexer = Lexer(code)
    if print_flag:
        lexer.printTokens()
        print()
    if save_flag:
        output_file = ARTIFACTS_FOLDER / f"{file_name}_tokens.txt"
        lexer.saveTokens(output_file)
    return lexer


def parser_analysis(lexer: Lexer, save_flag=False, print_flag=False) -> Parser:
    parser: Parser = Parser(lexer.tokens)
    if print_flag:
        parser.ast.print_tree()
        print()
    if save_flag:
        output_file = ARTIFACTS_FOLDER / f"{file_name}_AST.json"
        parser.ast.save_tree(output_file)
    return parser


def carregar_arquivo(caminho_codigo: Path) -> str:
    if not caminho_codigo.exists():
        raise Exception(f"Arquivo não encontrado: {caminho_codigo}")

    if not caminho_codigo.is_file():
        raise Exception(f"Caminho inválido (não é arquivo): {caminho_codigo}")

    try:
        return caminho_codigo.read_text(encoding="utf-8")
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo: {e}")


if __name__ == "__main__":
    main()
