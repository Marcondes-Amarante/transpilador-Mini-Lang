from lexer import Lexer, LexicalError
from parser import Parser, MiniLangSyntaxError
from semantic import Semantic, SemanticError, CGenerator

from pathlib import Path
import sys

ARTIFACTS_FOLDER = Path("./artifacts")
file_name = "arquivo"


def main():
    global file_name

    args_list: list[str] = sys.argv
    if len(args_list) < 2:
        print("Uso: python main.py <codigo_fonte>.txt [-save] [-print] [-nocode]")
        return

    try:
        caminho: Path = Path(args_list[1])
        codigo_fonte: str = carregar_arquivo(caminho)
        file_name = caminho.stem

        save_flag = "-save" in args_list
        print_flag = "-print" in args_list
        no_code = "-nocode" in args_list

        if save_flag:
            ARTIFACTS_FOLDER.mkdir(parents=True, exist_ok=True)

        lexer: Lexer = lexer_analysis(codigo_fonte, save_flag, print_flag)
        parser: Parser = parser_analysis(lexer, save_flag, print_flag)
        Semantic(parser.ast)

        print("\n ✓ Códigos léxico, sintático e tipos validados!")
        if (not no_code):
            print_c_code_menu(parser)
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


def print_c_code_menu(parser: Parser):
    print("\nDeseja gerar o equivalente do código em C?")
    print("1. Printar e salvar")
    print("2. Apenas printar")
    print("3. Apenas salvar")
    print("4. Não")

    while True:
        op_input = input(">> ").strip()
        if op_input.isdigit():
            op = int(op_input)
            if 1 <= op <= 4:
                break
        print("Opção inválida. Digite um número de 1 a 4.")

    save_flag, print_flag = False, False
    match op:
        case 1:
            save_flag, print_flag = True, True
        case 2:
            print_flag = True
        case 3:
            save_flag = True
    if op != 4:
        print("\nGerando código C...\n")
        translate(parser, save_flag, print_flag)


def translate(parser: Parser, save_flag=False, print_flag=False) -> None:
    gerador = CGenerator(parser.ast)
    if print_flag:
        gerador.print_code()
    if save_flag:
        ARTIFACTS_FOLDER.mkdir(parents=True, exist_ok=True)
        output_file = ARTIFACTS_FOLDER / f"{file_name}_c_code.c"
        gerador.save_code(output_file)


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
