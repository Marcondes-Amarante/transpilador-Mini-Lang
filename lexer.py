class Token:
    def __init__(self, tipo, valor, linha):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha

class Lexer:
    def __init__(self, codigo):
        self.codigo = codigo
        self.pos = 0
        self.linha = 1
        
        if self.codigo:
            self.caractere_atual = self.codigo[0]
        else:
            self.caractere_atual = None

        self.palavras_reservadas = {"def":"DEF", "while":"WHILE", "if":"IF", 
                                    "return":"RETURN", "print":"PRINT", "int":"INT_TYPE",
                                    "real":"REAL_TYPE", "bool":"BOOL_TYPE", "void":"VOID_TYPE",
                                    "var":"VAR", "set":"SET", "not":"NOT", "or":"OR", "and":"AND",
                                    "true":"BOOLEAN_LITERAL", "false":"BOOLEAN_LITERAL", 
                                    }
        
        self.op_aritmetricos = {"+":"PLUS", "-":"MINUS", "*":"MULTIPLY", "/":"DIVIDE"}

        self.delimitadores = {"{":"LBRACE", "}":"RBRACE", "(":"LPAREN", ")":"RPAREN", ":":"COLON",
                              ";":"SEMICOLON", ",":"COMMA"}

    #consome próximo caractere
    def avancar(self):
        self.pos += 1

        if self.pos < len(self.codigo):
            self.caractere_atual = self.codigo[self.pos]
        else:
            self.caractere_atual = None
    
    #verifica próximo caractere sem consumi-lo
    def lookahead(self):
        indice_proximo = self.pos + 1

        if indice_proximo < len(self.codigo):
            return self.codigo[indice_proximo]
        else:
            return None
    
    #tratando espaços e quebras de linha
    def ignorar_espacos(self):
        while self.caractere_atual and self.caractere_atual.isspace():
            if self.caractere_atual == "\n":
                self.linha += 1
            self.avancar()

    #tratando comentários
    def ignorar_comentario(self):
        while self.caractere_atual and self.caractere_atual !="\n":
            self.avancar()
        
    #funções reconhecedoras:

    #recupera literais inteiros e reais
    def read_numbers(self):

        result = ""

        #captura primeira parte de digitos
        while self.caractere_atual and self.caractere_atual.isdigit():
            result += self.caractere_atual
            self.avancar()

        #verifica se após os digitos lidos há um ponto
        if self.caractere_atual and self.caractere_atual == ".":
            result += self.caractere_atual
            self.avancar()

            #verifica se há mais digitos após o ponto
            if self.caractere_atual.isdigit():
                while self.caractere_atual and self.caractere_atual.isdigit():
                    result += self.caractere_atual
                    self.avancar()

                return Token("REAL_LITERAL", result, self.linha)
            
            else:
                raise Exception(f"caractere real mal formatado na linha: {self.linha}")
        
        else:
            return Token("INTEGER_LITERAL", result, self.linha)
            
    #Recupera literal string
    def read_string(self):
        
        result = ""

        #verifica se inica com aspas
        if self.caractere_atual == '"':
            self.avancar()

            #consome todos os caracter intermediários
            while self.caractere_atual is not None and self.caractere_atual != '"':
                result += self.caractere_atual
                self.avancar()

            if self.caractere_atual == '"':
                self.avancar()
            elif self.caractere_atual is None:
                raise Exception(f"delimitador de string não fechado na linha: {self.linha}")

            
            return Token("STRING_LITERAL", result, self.linha)

    #recupera identificadores, palavras reservadas, tipos, literal booleanos, operador NOT, OR e AND
    def read_identifier(self):
        
        result = ""

        if self.caractere_atual and (self.caractere_atual.isalpha() or self.caractere_atual == "_"):
            result += self.caractere_atual
            self.avancar()

            while self.caractere_atual and (self.caractere_atual.isalpha() or self.caractere_atual.isdigit() or self.caractere_atual == "_"):
                result += self.caractere_atual
                self.avancar()
        
        if result in self.palavras_reservadas:
            return Token(self.palavras_reservadas[result], result, self.linha)
        else:
            return Token("IDENTIFIER", result, self.linha)

    #despachante:
    def get_next_token(self):
        
        while self.caractere_atual is not None:

            if self.caractere_atual.isspace():
                self.ignorar_espacos()
                continue

            if self.caractere_atual == "#" or (self.caractere_atual == "/" and self.lookahead() == "/"):
                self.ignorar_comentario()
                continue

            if self.caractere_atual.isdigit():
                return self.read_numbers()
            
            if self.caractere_atual.isalpha() or self.caractere_atual == "_":
                return self.read_identifier()
            
            if self.caractere_atual == '"':
                return self.read_string()
            
            #trantando operadores de comparação (simples e composto)
            # == != >= <= | = < >
            if self.caractere_atual == "=":
                if self.lookahead() == "=":
                    self.avancar()
                    self.avancar()
                    return Token("EQUAL", "==", self.linha)
                else:
                    self.avancar()
                    return Token("ASSIGN", "=", self.linha)
            
            if self.caractere_atual == "!":
                if self.lookahead() == "=":
                    self.avancar()
                    self.avancar()
                    return Token("NOT_EQUAL", "!=", self.linha)
                else:
                    raise Exception("operador inválido: !")
            
            if self.caractere_atual == ">":
                if self.lookahead() == "=":
                    self.avancar()
                    self.avancar()
                    return Token("GREATER_EQUAL", ">=", self.linha)
                else:
                    self.avancar()
                    return Token("GREATER", ">", self.linha)
                
            if self.caractere_atual == "<":
                if self.lookahead() == "=":
                    self.avancar()
                    self.avancar()
                    return Token("LESS_EQUAL", "<=", self.linha)
                else:
                    self.avancar()
                    return Token("LESS", "<", self.linha)

            #trantando operadores aritmétricos simples
            # + - * /
            if self.caractere_atual in self.op_aritmetricos:
                result = self.caractere_atual
                linha = self.linha
                self.avancar()
                return Token(self.op_aritmetricos[result], result, linha)
            
            #tratando delimitadores
            if self.caractere_atual in self.delimitadores:
                result = self.caractere_atual
                linha = self.linha
                self.avancar()
                return Token(self.delimitadores[result], result, linha)

            #trantando caracteres inválidos
            raise Exception(f"caractere inválido: {self.caractere_atual}, na linha: {self.linha}")


        return Token("EOF", None, self.linha)