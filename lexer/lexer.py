RESERVED_KEYWORDS: dict[str, str] = {
    "def": "DEF",
    "while": "WHILE",
    "if": "IF",
    "return": "RETURN",
    "print": "PRINT",
    "int": "INT_TYPE",
    "real": "REAL_TYPE",
    "bool": "BOOL_TYPE",
    "void": "VOID_TYPE",
    "var": "VAR",
    "set": "SET",
    "not": "NOT",
    "or": "OR",
    "and": "AND",
    "true": "BOOLEAN_LITERAL",
    "false": "BOOLEAN_LITERAL",
}

ARITHMETIC_OPERATOS: dict[str, str] = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "MULTIPLY",
    "/": "DIVIDE",
}

DELIMITERS: dict[str, str] = {
    "{": "LBRACE",
    "}": "RBRACE",
    "(": "LPAREN",
    ")": "RPAREN",
    ":": "COLON",
    ";": "SEMICOLON",
    ",": "COMMA",
}


class Token:
    def __init__(self, tipo: str, valor: str, linha: int):
        self.__tipo: str = tipo
        self.__valor: str = valor
        self.__linha: int = linha
    
    @property
    def tipo(self) -> str:
        return self.__tipo
    
    @property
    def valor(self) -> str:
        return self.__valor
    
    @property
    def linha(self) -> int:
        return self.__linha
    
    def __repr__(self) -> str:
        return f"Token({self.__tipo}, {self.__valor}, {self.__linha})"
    
    def __str__(self) -> str:
        return f"<{self.__tipo}, {self.__valor}>"


class Lexer:
    def __init__(self, codigo: str):
        self._codigo: str = codigo
        self.__pos: int = 0
        self.__linha: int = 1
        if self._codigo:
            self.caractere_atual = self._codigo[0]
        else:
            self.caractere_atual = None
        self._tokens: list[Token] = self.__get_token_list()
        
    @property
    def tokens(self) -> tuple[Token]:
        return tuple(self._tokens)
    
    def printTokens(self) -> None:
        for token in self._tokens:
            print(token)

    # consome próximo caractere
    def __avancar(self) -> None:
        self.__pos += 1

        if self.__pos < len(self._codigo):
            self.caractere_atual = self._codigo[self.__pos]
        else:
            self.caractere_atual = None

    # verifica próximo caractere sem consumi-lo
    def __lookahead(self) -> str | None:
        indice_proximo = self.__pos + 1

        if indice_proximo < len(self._codigo):
            return self._codigo[indice_proximo]
        else:
            return None

    # tratando espaços e quebras de linha
    def __ignorar_espacos(self) -> None:
        while self.caractere_atual and self.caractere_atual.isspace():
            if self.caractere_atual == "\n":
                self.__linha += 1
            self.__avancar()

    # tratando comentários
    def __ignorar_comentario(self) -> None:
        while self.caractere_atual and self.caractere_atual != "\n":
            self.__avancar()

    # funções reconhecedoras:

    # recupera literais inteiros e reais
    def __read_numbers(self) -> Token:
        result: str = ""
        # captura primeira parte de digitos
        while self.caractere_atual and self.caractere_atual.isdigit():
            result += self.caractere_atual
            self.__avancar()
        # verifica se após os digitos lidos há um ponto
        if self.caractere_atual and self.caractere_atual == ".":
            result += self.caractere_atual
            self.__avancar()
            # verifica se há mais digitos após o ponto
            if self.caractere_atual.isdigit():
                while self.caractere_atual and self.caractere_atual.isdigit():
                    result += self.caractere_atual
                    self.__avancar()
                return Token("REAL_LITERAL", result, self.__linha)
            else:
                raise Exception(f"Caractere real mal formatado na linha: {self.__linha}")
        else:
            return Token("INTEGER_LITERAL", result, self.__linha)

    # Recupera literal string
    def __read_string(self) -> Token:
        result = ""
        # verifica se inica com aspas
        if self.caractere_atual == '"':
            self.__avancar()
            # consome todos os caracter intermediários
            while self.caractere_atual is not None and self.caractere_atual != '"':
                result += self.caractere_atual
                self.__avancar()
            if self.caractere_atual == '"':
                self.__avancar()
            elif self.caractere_atual is None:
                raise Exception(
                    f"Delimitador de string não fechado na linha: {self.__linha}"
                )
            return Token("STRING_LITERAL", result, self.__linha)

    # recupera identificadores, palavras reservadas, tipos, literal booleanos, operador NOT, OR e AND
    def __read_identifier(self) -> Token:
        result = ""
        if self.caractere_atual and (
            self.caractere_atual.isalpha() or self.caractere_atual == "_"
        ):
            result += self.caractere_atual
            self.__avancar()
            while self.caractere_atual and (
                self.caractere_atual.isalpha()
                or self.caractere_atual.isdigit()
                or self.caractere_atual == "_"
            ):
                result += self.caractere_atual
                self.__avancar()
        if result in RESERVED_KEYWORDS:
            return Token(RESERVED_KEYWORDS[result], result, self.__linha)
        else:
            return Token("IDENTIFIER", result, self.__linha)

    # despachante:
    def __get_next_token(self) -> Token:
        while self.caractere_atual is not None:
            if self.caractere_atual.isspace():
                self.__ignorar_espacos()
                continue

            if self.caractere_atual == "#" or (
                self.caractere_atual == "/" and self.__lookahead() == "/"
            ):
                self.__ignorar_comentario()
                continue

            if self.caractere_atual.isdigit():
                return self.__read_numbers()

            if self.caractere_atual.isalpha() or self.caractere_atual == "_":
                return self.__read_identifier()

            if self.caractere_atual == '"':
                return self.__read_string()

            # trantando operadores de comparação (simples e composto)
            # == != >= <= | = < >
            if self.caractere_atual == "=":
                if self.__lookahead() == "=":
                    self.__avancar()
                    self.__avancar()
                    return Token("EQUAL", "==", self.__linha)
                else:
                    self.__avancar()
                    return Token("ASSIGN", "=", self.__linha)

            if self.caractere_atual == "!":
                if self.__lookahead() == "=":
                    self.__avancar()
                    self.__avancar()
                    return Token("NOT_EQUAL", "!=", self.__linha)
                else:
                    raise Exception("operador inválido: !")

            if self.caractere_atual == ">":
                if self.__lookahead() == "=":
                    self.__avancar()
                    self.__avancar()
                    return Token("GREATER_EQUAL", ">=", self.__linha)
                else:
                    self.__avancar()
                    return Token("GREATER", ">", self.__linha)

            if self.caractere_atual == "<":
                if self.__lookahead() == "=":
                    self.__avancar()
                    self.__avancar()
                    return Token("LESS_EQUAL", "<=", self.__linha)
                else:
                    self.__avancar()
                    return Token("LESS", "<", self.__linha)

            # trantando operadores aritmétricos simples
            # + - * /
            if self.caractere_atual in ARITHMETIC_OPERATOS:
                result = self.caractere_atual
                linha = self.__linha
                self.__avancar()
                return Token(ARITHMETIC_OPERATOS[result], result, linha)

            # tratando delimitadores
            if self.caractere_atual in DELIMITERS:
                result = self.caractere_atual
                linha = self.__linha
                self.__avancar()
                return Token(DELIMITERS[result], result, linha)

            # trantando caracteres inválidos
            raise Exception(
                f"caractere inválido: {self.caractere_atual}, na linha: {self.__linha}"
            )

        return Token("EOF", None, self.__linha)

    def __get_token_list(self) -> list[Token]:
        tokens: list[Token] = []
        token: Token = self.__get_next_token()
        while token.tipo != "EOF":
            tokens.append(token)
            token = self.__get_next_token()
        return tokens
