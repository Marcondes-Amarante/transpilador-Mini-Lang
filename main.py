from lexer import Lexer

def carregar_arquivo(caminho_codigo):
    try:
        with open(caminho_codigo, 'r', encoding='utf=8') as codigo_fonte:
            return codigo_fonte.read()
    except FileNotFoundError:
        print("arquivo especificado não encontrado")
        return None
    
def main():
    codigo_fonte = carregar_arquivo("testes/testeErros.txt")

    if codigo_fonte:
        tokens = []
        lexer = Lexer(codigo_fonte)

        token = lexer.get_next_token()
        while token.tipo != "EOF":
            tokens.append(token)
            token = lexer.get_next_token()
        
        for token in tokens:
            print(f"<{token.tipo}, {token.valor}>")

if __name__ == "__main__":
    main()
