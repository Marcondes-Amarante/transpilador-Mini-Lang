from lexer import Token, TokenType
from .sintaxe_error import MiniLangSyntaxError
from .node import Node, NodeType
from .ast import AST


class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens: list[Token] = tokens
        self.__pos: int = 0
        self.__token_atual: Token = self._tokens[0]
        self.__ast: AST = AST(self.__parser_program())

    @property
    def ast(self) -> AST:
        return self.__ast

    # consumir token
    def __match(self, tipo: TokenType) -> None:
        if self.__token_atual and self.__token_atual.tipo == tipo:
            self.__pos += 1
            if self.__pos < len(self._tokens):
                self.__token_atual = self._tokens[self.__pos]
            else:
                self.__token_atual = None
        else:
            if self.__token_atual is not None:
                tipo_token = self.__token_atual.tipo
                linha = self.__token_atual.linha
            else:
                tipo_token = TokenType.EOF
                linha = -1
            raise MiniLangSyntaxError(
                f"Token do tipo {tipo.value} era esperado, recebeu: {tipo_token.value}",
                linha,
            )

    # retornar próximo token da lista sem consumi-lo
    def __lookahead(self) -> Token | None:
        pos_prox_token: int = self.__pos + 1
        if pos_prox_token < len(self._tokens):
            return self._tokens[pos_prox_token]
        else:
            return None

    # funções de parser para cada uma das regras da estrutura EBNF
    # padrão EBNF: {} -> while, [] -> if, () -> if, elif, else
    def __parser_program(self) -> Node:
        node = Node(NodeType.PROGRAM)
        while self.__token_atual is not None:
            stmt = self.__parser_statement()
            if stmt is not None:
                node.add_filho(stmt)
        return node

    def __parser_block(self) -> Node:
        node = Node(NodeType.BLOCK)

        self.__match(TokenType.LBRACE)
        while self.__token_atual and self.__token_atual.tipo != TokenType.RBRACE:
            stmt = self.__parser_statement()
            if stmt is not None:
                node.add_filho(stmt)
        self.__match(TokenType.RBRACE)

        return node

    def __parser_statement(self) -> Node:
        match self.__token_atual.tipo:
            case TokenType.VAR:
                node = self.__parser_variable_decl()
                self.__match(TokenType.SEMICOLON)
                return node
            case TokenType.SET:
                node = self.__parser_assignment()
                self.__match(TokenType.SEMICOLON)
                return node
            case TokenType.PRINT:
                node = self.__parser_print_statement()
                self.__match(TokenType.SEMICOLON)
                return node
            case TokenType.IF:
                return self.__parser_if_statement()
            case TokenType.WHILE:
                return self.__parser_while_statement()
            case TokenType.RETURN:
                node = self.__parser_return_statement()
                self.__match(TokenType.SEMICOLON)
                return node
            case TokenType.DEF:
                return self.__parser_function_decl()
            case TokenType.LBRACE:
                return self.__parser_block()
            case TokenType.IDENTIFIER:
                if self.__lookahead() and self.__lookahead().tipo == TokenType.LPAREN:
                    node = self.__parser_function_call()
                    self.__match(TokenType.SEMICOLON)
                    return node
                else:
                    raise MiniLangSyntaxError(
                        f"Statement inesperado: IDENTIFIER",
                        self.__token_atual.linha,
                    )
            case _:
                raise MiniLangSyntaxError(
                    f"Statement inesperado: {self.__token_atual.tipo.name}",
                    self.__token_atual.linha,
                )

    # <DEF, def> <IDENTIFIER, calcular> <LPAREN, (>

    def __parser_function_decl(self) -> Node:
        node = Node(NodeType.FUNCTION_DECL)

        self.__match(TokenType.DEF)
        node.add_filho(self.__parser_identifier())
        self.__match(TokenType.LPAREN)

        if self.__token_atual.tipo == TokenType.IDENTIFIER:
            node.add_filho(self.__parser_formal_params())

        self.__match(TokenType.RPAREN)
        self.__match(TokenType.COLON)

        node.add_filho(self.__parser_type())
        node.add_filho(self.__parser_block())

        return node

    def __parser_formal_params(self) -> Node:
        node = Node(NodeType.PARAM_LIST)

        node.add_filho(self.__parser_formal_param())
        while self.__token_atual and self.__token_atual.tipo != TokenType.RPAREN:
            self.__match(TokenType.COMMA)
            node.add_filho(self.__parser_formal_param())

        return node

    def __parser_formal_param(self) -> Node:
        node = Node(NodeType.PARAM)

        node.add_filho(self.__parser_identifier())
        self.__match(TokenType.COLON)
        node.add_filho(self.__parser_type())

        return node

    def __parser_while_statement(self) -> Node:
        node = Node(NodeType.WHILE_STMT)

        self.__match(TokenType.WHILE)
        self.__match(TokenType.LPAREN)
        node.add_filho(self.__parser_expression())
        self.__match(TokenType.RPAREN)
        node.add_filho(self.__parser_block())

        return node

    def __parser_if_statement(self) -> Node:
        node = Node(NodeType.IF_STMT)

        self.__match(TokenType.IF)
        self.__match(TokenType.LPAREN)
        node.add_filho(self.__parser_expression())
        self.__match(TokenType.RPAREN)

        node.add_filho(self.__parser_block())

        if self.__token_atual and self.__token_atual.tipo == TokenType.ELSE:
            self.__match(TokenType.ELSE)
            node.add_filho(self.__parser_block())

        return node

    def __parser_return_statement(self) -> Node:
        node = Node(NodeType.RETURN_STMT)

        self.__match(TokenType.RETURN)
        node.add_filho(self.__parser_expression())
        node.valor = self.__token_atual

        return node

    def __parser_print_statement(self) -> Node:
        node = Node(NodeType.PRINT_STMT)

        self.__match(TokenType.PRINT)
        if self.__token_atual and self.__token_atual.tipo == TokenType.STRING_LITERAL:
            node.add_filho(self.__parser_string_literal())
        else:
            node.add_filho(self.__parser_expression())

        return node

    # int | real | bool | void
    def __parser_type(self) -> Node:
        node = Node(NodeType.TYPE_STMT)

        token = self.__token_atual
        match token.tipo:
            case TokenType.INT_TYPE:
                self.__match(TokenType.INT_TYPE)
            case TokenType.REAL_TYPE:
                self.__match(TokenType.REAL_TYPE)
            case TokenType.BOOL_TYPE:
                self.__match(TokenType.BOOL_TYPE)
            case TokenType.VOID_TYPE:
                self.__match(TokenType.VOID_TYPE)
            case _:
                raise MiniLangSyntaxError(
                    f"Tipo inválido: {token.tipo.name}", token.linha
                )
        node.valor = token

        return node

    def __parser_variable_decl(self) -> Node:
        node = Node(NodeType.VAR_DECL)

        self.__match(TokenType.VAR)
        node.add_filho(self.__parser_identifier())
        self.__match(TokenType.COLON)
        node.add_filho(self.__parser_type())
        self.__match(TokenType.ASSIGN)
        node.add_filho(self.__parser_expression())

        return node

    def __parser_assignment(self) -> Node:
        node = Node(NodeType.ASSIGN_STMT)

        self.__match(TokenType.SET)
        node.add_filho(self.__parser_identifier())
        self.__match(TokenType.ASSIGN)
        node.add_filho(self.__parser_expression())

        return node

    def __parser_expression(self) -> Node:
        left = self.__parser_and()
        while self.__token_atual and self.__token_atual.tipo == TokenType.OR:
            token = self.__token_atual
            self.__match(token.tipo)

            right = self.__parser_and()
            node = Node(NodeType.BINARY_OP)
            node.valor = token
            node.add_filho(left)
            node.add_filho(right)
            left = node
        return left
    
    def __parser_and(self) -> Node:
        left = self.__parser_relational()
        while self.__token_atual and self.__token_atual.tipo == TokenType.AND:
            token = self.__token_atual
            self.__match(token.tipo)

            right = self.__parser_relational()
            node = Node(NodeType.BINARY_OP)
            node.valor = token
            node.add_filho(left)
            node.add_filho(right)
            left = node
        return left
    
    def __parser_relational(self) -> Node:
        left = self.__parser_simple_expression()

        relational_ops = {
            TokenType.LESS,
            TokenType.GREATER,
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
        }

        while self.__token_atual and self.__token_atual.tipo in relational_ops:
            token = self.__token_atual
            self.__match(token.tipo)

            right = self.__parser_simple_expression()
            node = Node(NodeType.BINARY_OP)
            node.valor = token
            node.add_filho(left)
            node.add_filho(right)
            left = node
        return left

    def __parser_simple_expression(self) -> Node:
        left = self.__parser_term()

        while self.__token_atual and self.__token_atual.tipo in {
            TokenType.PLUS,
            TokenType.MINUS,
        }:
            token = self.__token_atual
            self.__match(token.tipo)

            right = self.__parser_term()
            node = Node(NodeType.BINARY_OP)
            node.valor = token
            node.add_filho(left)
            node.add_filho(right)
            left = node
        return left

    def __parser_term(self) -> Node:
        left = self.__parser_factor()
        while self.__token_atual and self.__token_atual.tipo in {
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
        }:
            token = self.__token_atual
            self.__match(token.tipo)

            right = self.__parser_factor()
            node = Node(NodeType.BINARY_OP)
            node.valor = token
            node.add_filho(left)
            node.add_filho(right)
            left = node
        return left

    def __parser_factor(self) -> Node:
        token = self.__token_atual

        if token.tipo in {
            TokenType.INTEGER_LITERAL,
            TokenType.REAL_LITERAL,
            TokenType.BOOLEAN_LITERAL,
        }:
            return self.__parser_literal()

        elif token.tipo == TokenType.IDENTIFIER:
            if self.__lookahead() and self.__lookahead().tipo == TokenType.LPAREN:
                return self.__parser_function_call()
            else:
                return self.__parser_identifier()

        elif token.tipo == TokenType.LPAREN:
            return self.__parser_sub_expression()

        elif token.tipo in {
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.NOT,
        }:
            return self.__parser_unary()

        else:
            raise MiniLangSyntaxError(
                f"Factor inválido: {token.tipo.name}", token.linha
            )

    def __parser_unary(self) -> Node:
        token = self.__token_atual
        if token.tipo in {
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.NOT,
        }:
            self.__match(token.tipo)
            expr = self.__parser_unary()
            node = Node(NodeType.UNARY_OP)
            node.valor = token
            node.add_filho(expr)

            return node
        else:
            return self.__parser_factor()

    def __parser_sub_expression(self) -> Node:
        self.__match(TokenType.LPAREN)
        node = self.__parser_expression()
        self.__match(TokenType.RPAREN)
        return node

    def __parser_function_call(self) -> Node:
        node = Node(NodeType.FUNCTION_CALL)

        node.add_filho(self.__parser_identifier())

        self.__match(TokenType.LPAREN)
        if self.__token_atual and self.__token_atual.tipo != TokenType.RPAREN:
            node.add_filho(self.__parser_actual_params())
        self.__match(TokenType.RPAREN)

        return node

    def __parser_actual_params(self) -> Node:
        node = Node(NodeType.ARG_LIST)

        node.add_filho(self.__parser_expression())
        while self.__token_atual and self.__token_atual.tipo == TokenType.COMMA:
            self.__match(TokenType.COMMA)
            node.add_filho(self.__parser_expression())

        return node

    """def parser_relational_op(self) -> Node:
        node = Node(NodeType.BINARY_OP)
        token = self.__token_atual

        match token.tipo:
            case TokenType.LESS:
                self.__match(TokenType.LESS)
            case TokenType.GREATER:
                self.__match(TokenType.GREATER)
            case TokenType.EQUAL:
                self.__match(TokenType.EQUAL)
            case TokenType.NOT_EQUAL:
                self.__match(TokenType.NOT_EQUAL)
            case TokenType.LESS_EQUAL:
                self.__match(TokenType.LESS_EQUAL)
            case TokenType.GREATER_EQUAL:
                self.__match(TokenType.GREATER_EQUAL)
            case _:
                raise MiniLangSyntaxError(
                    f"Operador relacional inválido: {token.tipo.name}", token.linha
                )

        node.valor = token
        return node

    def parser_aditive_op(self) -> Node:
        node = Node(NodeType.BINARY_OP)
        token = self.__token_atual

        match token.tipo:
            case TokenType.PLUS:
                self.__match(TokenType.PLUS)
            case TokenType.MINUS:
                self.__match(TokenType.MINUS)
            case TokenType.OR:
                self.__match(TokenType.OR)
            case _:
                raise MiniLangSyntaxError(
                    f"Operador aditivo inválido: {token.tipo.name}", token.linha
                )
        node.valor = token
        return node

    def parser_multiplicative_op(self) -> Node:
        node = Node(NodeType.BINARY_OP)
        token = self.__token_atual

        match token.tipo:
            case TokenType.MULTIPLY:
                self.__match(TokenType.MULTIPLY)
            case TokenType.DIVIDE:
                self.__match(TokenType.DIVIDE)
            case TokenType.AND:
                self.__match(TokenType.AND)
            case _:
                raise MiniLangSyntaxError(
                    f"Operador multiplicativo inválido: {token.tipo.name}", token.linha
                )
        node.valor = token
        return node"""

    def __parser_identifier(self):
        node = Node(NodeType.IDENTIFIER)
        token = self.__token_atual

        self.__match(TokenType.IDENTIFIER)

        node.valor = token
        return node

    def __parser_string_literal(self):
        node = Node(NodeType.LITERAL)
        token = self.__token_atual

        self.__match(TokenType.STRING_LITERAL)

        node.valor = token
        return node

    def __parser_literal(self) -> Node:
        node = Node(NodeType.LITERAL)
        token = self.__token_atual

        if token.tipo in {
            TokenType.INTEGER_LITERAL,
            TokenType.REAL_LITERAL,
            TokenType.BOOLEAN_LITERAL,
        }:
            self.__match(token.tipo)
            node.valor = token
            return node
        else:
            raise MiniLangSyntaxError(
                f"Literal inválido: {token.tipo.name}", token.linha
            )
