from lexer import TokenType
from parser import AST, Node
from .semantic_error import SemanticError


class Semantic:

    def __init__(self, ast: AST):
        self.__ast: AST = ast
        # lista contendo tabela de símbolos para escopos
        # o primeiro item é a tabela do escopo global, e a última a do escopo atual
        self.scope = [{}]
        self.visita(ast.raiz)
        self.aux_has_return = False
        self.aux_curr_func_type = ""

    # retorna o método do analisador semantico relativo ao tipo do no
    def visita(self, No: Node):

        tipoNo: str = f"visitor_{No.tipo.value}"
        # print(f"[DEBUG] Visitando nó: {No.tipo} (procurando {tipoNo})")
        metodo = getattr(self, tipoNo, self.visita_padrao)
        # print(f"[DEBUG] Método encontrado: {metodo.__name__}")
        return metodo(No)

    # visita padrão para caso não exista visitor específico para o tipo do No
    def visita_padrao(self, No: Node):

        for filho in No.filhos:
            self.visita(filho)

    # funções visitor para as regras da gramática
    # ex: visitor_variable_decl()
    # funções visitor vão adicionar coisas no escopo atual, verificar se objeto existe em algum escopo
    # verificar tipo de expressão

    def visitor_LITERAL(self, no: Node) -> str:
        token_tipo: TokenType = no.valor.tipo

        if token_tipo == TokenType.INTEGER_LITERAL:
            return "int"
        if token_tipo == TokenType.REAL_LITERAL:
            return "real"
        if token_tipo == TokenType.BOOLEAN_LITERAL:
            return "bool"
        if token_tipo == TokenType.STRING_LITERAL:
            return "string"

        return "void"

    def visitor_IDENTIFIER(self, no: Node):
        nome_var: str = no.valor.valor
        # print(f"[DEBUG] Procurando '{nome_var}' nos escopos: {self.scope}")

        for escopo in reversed(self.scope):
            if nome_var in escopo:
                valor = escopo[nome_var]
                if isinstance(valor, dict):
                    return valor["tipo"]
                return valor
        # print(f"[DEBUG] '{nome_var}' NÃO ENCONTRADA!")

        raise SemanticError(f"Identificador '{nome_var}' não declarado", no.valor.linha)

    def visitor_TYPE_STMT(self, no: Node):
        return no.valor.valor

    def visitor_VAR_DECL(self, no: Node):
        ident = no.filhos[0]
        tipo_node = no.filhos[1]
        expr = no.filhos[2]

        nome_var = ident.valor.valor
        tipo_declarado = tipo_node.valor.valor
        tipo_expressao = self.visita(expr)

        if not self._sao_compativeis(tipo_declarado, tipo_expressao):
            raise SemanticError(
                f"Erro: {tipo_declarado} != {tipo_expressao}", ident.valor.linha
            )

        if nome_var in self.scope[-1]:
            raise SemanticError(
                f"Variável '{nome_var}' já declarada neste escopo", ident.valor.linha
            )

        self.scope[-1][nome_var] = tipo_declarado

    def visitor_ASSIGN_STMT(self, no: Node):
        ident = no.filhos[0]
        expr = no.filhos[1]

        nome_var = ident.valor.valor
        # print(f"[DEBUG] ASSIGN_STMT para '{nome_var}'")
        tipo_variavel = self.visita(ident)
        tipo_expressao = self.visita(expr)

        # print(f"[DEBUG] Tipo de '{nome_var}': {tipo_variavel}, Tipo da expr: {tipo_expressao}")

        if not self._sao_compativeis(tipo_variavel, tipo_expressao):
            raise SemanticError(
                f"Erro: não pode atribuir {tipo_expressao} em {tipo_variavel}",
                ident.valor.linha,
            )

    def visitor_BINARY_OP(self, no: Node):
        esq = no.filhos[0]
        dir = no.filhos[1]

        tipo_esq = self.visita(esq)
        tipo_dir = self.visita(dir)
        op = no.valor.tipo

        if op in {
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
        }:
            if tipo_esq == "int" and tipo_dir == "int":
                return "int"
            if tipo_esq in ["int", "real"] and tipo_dir in ["int", "real"]:
                return "real"
            raise SemanticError(
                f"Operação inválida: {tipo_esq} {op.name} {tipo_dir}", no.valor.linha
            )

        if op in {
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.LESS,
            TokenType.GREATER,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
        }:
            if tipo_esq == tipo_dir:
                return "bool"
            if tipo_esq in ["int", "real"] and tipo_dir in ["int", "real"]:
                return "bool"
            raise SemanticError(f"Comparação inválida", no.valor.linha)

        if op in {TokenType.AND, TokenType.OR}:
            if tipo_esq == "bool" and tipo_dir == "bool":
                return "bool"
            raise SemanticError(f"Operação lógica inválida", no.valor.linha)

    def visitor_UNARY_OP(self, no: Node):
        expr = no.filhos[0]
        tipo = self.visita(expr)
        op = no.valor.tipo

        if op == TokenType.NOT:
            if tipo != "bool":
                raise SemanticError(f"NOT precisa de bool", no.valor.linha)
            return "bool"

        if op in {TokenType.PLUS, TokenType.MINUS}:
            if tipo in ["int", "real"]:
                return tipo
            raise SemanticError(f"Operador inválido", no.valor.linha)

    def visitor_IF_STMT(self, no: Node):
        cond = no.filhos[0]
        bloco_if = no.filhos[1]

        tipo_cond = self.visita(cond)

        if tipo_cond != "bool":
            raise SemanticError(f"IF precisa de bool", no.valor.linha)

        self.visita(bloco_if)

        if len(no.filhos) > 2:
            self.visita(no.filhos[2])

    def visitor_WHILE_STMT(self, no: Node):
        cond = no.filhos[0]
        bloco = no.filhos[1]

        tipo_cond = self.visita(cond)

        if tipo_cond != "bool":
            raise SemanticError(f"WHILE precisa de bool", no.valor.linha)

        self.visita(bloco)

    def visitor_FUNCTION_DECL(self, no: Node):
        self.aux_has_return = False
        ident = no.filhos[0]
        nome_funcao = ident.valor.valor

        tipo_node = no.filhos[-2]
        tipo_retorno = tipo_node.valor.valor

        param_tipos = []
        param_names = set()
        if len(no.filhos) > 3:
            param_list = no.filhos[1]
            for param in param_list.filhos:
                nome_param = param.filhos[0].valor.valor
                tipo_param = param.filhos[1].valor.valor
                param_tipos.append(tipo_param)
                if nome_param in param_names:
                    raise SemanticError(
                        f"Parâmetro '{nome_param}' já declarada na função",
                        ident.valor.linha,
                    )
                param_names.add(nome_param)
                self.scope[-1][nome_param] = tipo_param
        self.scope[-1][nome_funcao] = {"tipo": tipo_retorno, "params": param_tipos}
        self.scope.append({})

        self.aux_curr_func_type = tipo_retorno
        self.visita(no.filhos[-1])

        if tipo_retorno != "void" and not self.aux_has_return:
            raise SemanticError(
                f"Função '{nome_funcao}' deve retornar um valor do tipo {tipo_retorno}",
                ident.valor.linha,
            )

        self.scope.pop()

    def visitor_RETURN_STMT(self, no: Node):
        self.aux_has_return = True
        expr = no.filhos[0]
        tipo_retorno = self.visita(expr)
        if not self._sao_compativeis(self.aux_curr_func_type, tipo_retorno):
            raise SemanticError(
                f"Retorno inválido: esperado {self.aux_curr_func_type}, recebido {tipo_retorno}",
                no.valor.linha
            )
        return tipo_retorno

    def visitor_FUNCTION_CALL(self, no: Node):
        nome = no.filhos[0].valor.valor
        linha = no.filhos[0].valor.linha

        for escopo in reversed(self.scope):
            if nome in escopo:
                func = escopo[nome]
                break
        else:
            raise SemanticError(f"Função '{nome}' não declarada", linha)

        tipos_params = func["params"]

        args = []
        if len(no.filhos) > 1:
            for arg in no.filhos[1].filhos:
                args.append(self.visita(arg))

        if len(args) != len(tipos_params):
            raise SemanticError(
                f"Função '{nome}' espera {len(tipos_params)} argumentos, mas recebeu {len(args)}",
                linha,
            )

        for i in range(len(args)):
            if not self._sao_compativeis(tipos_params[i], args[i]):
                raise SemanticError(
                    f"Argumento {i+1} inválido: esperado {tipos_params[i]}, recebido {args[i]}",
                    linha,
                )

        return func["tipo"]

    def visitor_PROGRAM(self, no):
        for filho in no.filhos:
            self.visita(filho)

    def visitor_BLOCK(self, no):
        self.scope.append({})

        for filho in no.filhos:
            self.visita(filho)

        self.scope.pop()

    def visitor_PRINT_STMT(self, no):
        self.visita(no.filhos[0])

    def visitor_PARAM(self, no):
        """Visitor para nó PARAM (parâmetro de função)"""
        return self.visita_padrao(no)

    def visitor_PARAM_LIST(self, no):
        """Visitor para nó PARAM_LIST (lista de parâmetros)"""
        return self.visita_padrao(no)

    def visitor_ARG_LIST(self, no):
        """Visitor para nó ARG_LIST (lista de argumentos)"""
        for arg in no.filhos:
            self.visita(arg)

    def _sao_compativeis(self, tipo_alvo, tipo_dado):
        if tipo_alvo == tipo_dado:
            return True
        if tipo_alvo == "real" and tipo_dado == "int":
            return True
        return False
