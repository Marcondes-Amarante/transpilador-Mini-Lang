from lexer import Lexer, LexicalError
from parser import Parser, AST
import sys


def main():
    args_list: list[str] = sys.argv
    if len(args_list) < 2:
        print("Uso: python main.py <codigo_fonte>.txt")
        return
    caminho: str = args_list[1]
    codigo_fonte: str = carregar_arquivo(caminho)
    if not codigo_fonte:
        raise Exception("Arquivo fonte vazio")
    try:
        lexer: Lexer = Lexer(codigo_fonte)
        lexer.printTokens()
    except LexicalError as e:
        print(e)


def carregar_arquivo(caminho_codigo) -> str:
    try:
        with open(caminho_codigo, "r", encoding="utf=8") as codigo_fonte:
            return codigo_fonte.read()
    except FileNotFoundError:
        print("arquivo especificado não encontrado")
        return None


if __name__ == "__main__":
    main()
