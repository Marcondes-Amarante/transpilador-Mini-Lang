class AST:
    def __init__(self, raiz):
        self.raiz = raiz

class No:
    def __init__(self, valor, tipo):
        self.tipo = tipo
        self.valor = valor
        self.filhos = []

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_atual = self.tokens[0]

    #tokens[0]: <ID, numero>

    #consumir token
    def match(self, tipo):
        if self.token_atual and self.token_atual.tipo == tipo:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.token_atual = self.tokens[self.pos]
            else:
                self.token_atual = None
        else:
            if self.token_atual.tipo:
                tipo_token = self.token_atual.tipo
            else:
                tipo_token = "EOF"
            raise Exception(f"token do tipo: {tipo} esperado, recebeu: {tipo_token}")

    #retornar próximo token da lista sem consumi-lo
    def lookahead(self):
        pos_prox_token = self.pos + 1
        if pos_prox_token < len(self.tokens):
            return self.tokens[pos_prox_token]
        else:
            return None

    #funções de parser para cada uma das regras da estrutura EBNF
    #padrão EBNF: {} -> while, [] -> if, () -> if, elif, else
    def parser_program(self):

        statements = []
        while self.token_atual is not None:
            statements.append(self.parser_statement())
    
    def parser_block(self):
        self.match("LBRACE")

        statements = []
        while self.token_atual and self.token_atual.tipo != "RBRACE":
            statements.append(self.parser_statement())

        self.match("RBRACE")

    def parser_statement(self):
        if self.token_atual.tipo == "VAR":
            self.parser_variable_decl()
            self.match("SEMICOLON")
        elif self.token_atual.tipo == "SET":
            self.parser_assignment()
            self.match("SEMICOLON")
        elif self.token_atual.tipo == "PRINT":
            self.parser_print_statement()
            self.match("SEMICOLON")
        elif self.token_atual.tipo == "IF":
            self.parser_if_statement()
        elif self.token_atual.tipo == "WHILE":
            self.parser_while_statement()
        elif self.token_atual.tipo == "RETURN":
            self.parser_return_statement()
            self.match("SEMICOLON")
        elif self.token_atual.tipo == "DEF":
            self.parser_function_decl()
        elif self.token_atual.tipo == "LBRACE":
            self.parser_block()

    # <DEF, def> <IDENTIFIER, calcular> <LPAREN, (> 

    def parser_function_decl(self):
        self.match("DEF")
        self.parser_identifier()

        self.match("LPAREN")
        if self.token_atual.tipo == "IDENTIFIER":
            self.parser_formal_params()
        self.match("RPAREN")
        
        self.match("COLON")
        self.parser_type()
        self.parser_block()

    def parser_formal_params(self):
        self.parser_formal_param()

        parametros = []
        while self.token_atual and self.token_atual.tipo != "RPAREN":
            self.match("COMMA")
            parametros.append(self.parser_formal_param())

    def parser_formal_param(self):
        self.parser_identifier()
        self.match("COLON")
        self.parser_type()
    
    def parser_while_statement(self):
        self.match("WHILE")
        self.match("LPAREN")
        self.parser_expression()
        self.match("RPAREN")
        self.parser_block()
    
    def parser_if_statement(self):
        self.match("IF")
        
        self.match("LPAREN")
        self.parser_expression()
        self.match("RPAREN")

        self.parser_block()

        if self.token_atual and self.token_atual.tipo == "ELSE":
            self.match("ELSE")
            self.parser_block()

    def parser_return_statement(self):
        self.match("RETURN")
        self.parser_expression()

    def parser_print_statement(self):
        self.match("PRINT")
        self.parser_string_literal()

    #int | real | bool | void
    def parser_type(self):
        if self.token_atual.tipo == "INT_TYPE":
            self.match("INT_TYPE")
        elif self.token_atual.tipo == "REAL_TYPE":
            self.match("REAL_TYPE")
        elif self.token_atual.tipo == "BOOL_TYPE":
            self.match("BOOL_TYPE")
        elif self.token_atual.tipo == "VOID_TYPE":
            self.match("VOID_TYPE")
    
    def parser_variable_decl(self):
        self.match("VAR")
        self.parser_identifier()
        self.match("COLON")
        self.parser_type()
        self.match("ASSIGN")
        self.parser_expression()

    def parser_assignment(self):
        self.match("SET")
        self.parser_identifier()
        self.match("ASSIGN")
        self.parser_expression()

    def parser_expression(self):
        self.parser_simple_expression()

        relational_op = ["LESS", "GREATER", "EQUAL", "NOT_EQUAL", "LESS_EQUAL", "GREATER_EQUAL"]

        while self.token_atual and self.token_atual.tipo in relational_op:
            self.parser_relational_op()
            self.parser_simple_expression()

    def parser_simple_expression(self):
        self.parser_term()

        aditive_op = ["PLUS", "MINUS", "OR"]

        while self.token_atual and self.token_atual.tipo in aditive_op:
            self.parser_aditive_op()
            self.parser_term()
    
    def parser_term(self):
        self.parser_factor()

        multiplicative_op = ["MULTIPLY", "DIVIDE", "AND"]

        while self.token_atual and self.token_atual.tipo in multiplicative_op:
            self.parser_multiplicative_op()
            self.parser_factor()
        
    def parser_factor(self):

        if self.token_atual.tipo in ["INTEGER_LITERAL", "REAL_LITERAL", "BOOLEAN_LITERAL"]:
            self.parser_literal()
        
        if self.token_atual.tipo == "IDENTIFIER":

            if self.lookahead() and self.lookahead().tipo == "LPAREN":
                self.parser_function_call()
            else:
                self.parser_identifier()

        if self.token_atual.tipo == "LPAREN":
            self.parser_sub_expression()
        
        if self.token_atual.tipo in ["PLUS", "MINUS", "NOT"]:
            self.parser_unary()
    
    def parser_unary(self):
        if self.token_atual.tipo == "PLUS":
            self.match("PLUS")
        elif self.token_atual.tipo == "MINUS":
            self.match("MINUS")
        elif self.token_atual.tipo == "NOT":
            self.match("NOT")

        #duvida: <expression> ou { <expression> } ou <factor>?
        self.parser_factor()
    
    def parser_sub_expression(self):
        self.match("LPAREN")
        self.parser_expression()
        self.match("RPAREN")
    
    def parser_function_call(self):
        self.parser_identifier()
        
        self.match("LPAREN")

        actual_param = []
        if self.token_atual and self.token_atual.tipo != "RPAREN":
            actual_param.append(self.parser_actual_params())

        self.match("RPAREN")
    
    def parser_actual_params(self):
        self.parser_expression()

        while self.token_atual and self.token_atual.tipo == "COMMA":
            self.match("COMMA")
            self.parser_expression()

    def parser_relational_op(self):
        if self.token_atual.tipo == "LESS":
            self.match("LESS")
        elif self.token_atual.tipo == "GREATER":
            self.match("GREATER")
        elif self.token_atual.tipo == "EQUAL":
            self.match("EQUAL")
        elif self.token_atual.tipo == "NOT_EQUAL":
            self.match("NOT_EQUAL")
        elif self.token_atual.tipo == "LESS_EQUAL":
            self.match("LESS_EQUAL")
        elif self.token_atual.tipo == "GREATER_EQUAL":
            self.match("GREATER_EQUAL")

    def parser_aditive_op(self):
        if self.token_atual.tipo == "PLUS":
            self.match("PLUS")
        elif self.token_atual.tipo == "MINUS":
            self.match("MINUS")
        elif self.token_atual.tipo == "OR":
            self.match("OR")

    def parser_multiplicative_op(self):
        if self.token_atual.tipo == "MULTIPLY":
            self.match("MULTIPLY")
        elif self.token_atual.tipo == "DIVIDE":
            self.match("DIVIDE")
        elif self.token_atual.tipo == "AND":
            self.match("AND")
    
    def parser_identifier(self):
        self.match("IDENTIFIER")

    def parser_literal(self):
        if self.token_atual.tipo in ["INTEGER_LITERAL", "REAL_LITERAL", "BOOL_LITERAL"]:
            self.match(self.token_atual.tipo)

        


