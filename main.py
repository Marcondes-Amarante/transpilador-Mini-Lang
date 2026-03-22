from lexer import Lexer, LexicalError
from parser import Parser, MiniLangSyntaxError
from semantic import AnalisadorSemantico
from C_generator import CGenerator
import os
import sys




def main():
    args_list: list[str] = sys.argv
    if len(args_list) < 2:
        print("Uso: python main.py <codigo_fonte>.txt")
        return
    caminho: str = args_list[1]
    codigo_fonte: str = carregar_arquivo(caminho)
    
    if not codigo_fonte:
        raise Exception(f"Arquivo {caminho} não encontrado ou vazio.")
    
    try:
    
        lexer: Lexer = Lexer(codigo_fonte)
        # lexer.printTokens()
        parser: Parser = Parser(lexer.tokens)
        # parser.ast.print_tree()
        analisador_semantico = AnalisadorSemantico()
        analisador_semantico.visita(parser.ast.raiz)
        #print("\n>>> Sucesso: Código léxico, sintático e tipos validados!")
        print("\n ✓ Códigos léxico, sintático e tipos validados!")
        print("\n Gerando código C... \n")
        gerador = CGenerator()
        codigo_c = gerador.generate(parser.ast.raiz)

        nome_arquivo_saída = os.path.splitext(caminho)[0]+".c"
        with open(nome_arquivo_saída, "w", encoding = "utf-8") as f: 
            f.write(codigo_c)

        print(f"✓ Código C gerado em: {nome_arquivo_saída}")
        print("\n --- CÓDIGO C GERADO --- \n")
        print(codigo_c)
    except LexicalError as e:
        print(e)
    except MiniLangSyntaxError as e:
        print(e)
    except Exception as e:
        print(f"Erro Semântico: {e}")




def carregar_arquivo(caminho_codigo) -> str:
    try:
        with open(caminho_codigo, "r", encoding="utf-8") as codigo_fonte:
            return codigo_fonte.read()
    except FileNotFoundError:
        print("arquivo especificado não encontrado")
        return None


if __name__ == "__main__":
    main()
