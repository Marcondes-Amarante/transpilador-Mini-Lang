class AnalisadorSemantico:

    def __init__(self):
        
        #lista contendo tabela de símbolos para escopos
        #o primeiro item é a tabela do escopo global, e a última a do escopo atual
        self.scope = [{}]

    #retorna o método do analisador semantico relativo ao tipo do no
    def visita(self, No):
            
        tipoNo = f"visitor_{No.tipo}"
        metodo = getattr(self, tipoNo, self.visita_padrao)
        return metodo(No)

    #visita padrão para caso não exista visitor específico para o tipo do No
    def visita_padrao(self, No):
            
        for filho in No.filhos:
            self.visita(filho)

    #funções visitor para as regras da gramática
    #ex: visitor_variable_decl()
    #funções visitor vão adicionar coisas no escopo atual, verificar se objeto existe em algum escopo
    #verificar tipo de expressão

   def visitor_LITERAL(self, no):
        token_tipo = no.valor.tipo

        if token_tipo == TokenType.INTEGER_LITERAL:
            return "int"
        if token_tipo == TokenType.REAL_LITERAL:
            return "real"
        if token_tipo == TokenType.BOOLEAN_LITERAL:
            return "bool"
        if token_tipo == TokenType.STRING_LITERAL:
            return "string"

        return "void"

    def visitor_IDENTIFIER(self, no):
        nome_var = no.valor.valor

        for escopo in reversed(self.scope):
            if nome_var in escopo:
                return escopo[nome_var]

        raise Exception(f"Variável '{nome_var}' não declarada")

    def visitor_TYPE_STMT(self, no):
        return no.valor.valor

    def visitor_VAR_DECL(self, no):
        ident = no.filhos[0]
        tipo_node = no.filhos[1]
        expr = no.filhos[2]

        nome_var = ident.valor.valor
        tipo_declarado = tipo_node.valor.valor
        tipo_expressao = self.visita(expr)

        if not self._sao_compativeis(tipo_declarado, tipo_expressao):
            raise Exception(
                f"[Linha {ident.valor.linha}] "
                f"Erro: {tipo_declarado} != {tipo_expressao}"
            )

        self.scope[-1][nome_var] = tipo_declarado

    def visitor_ASSIGN_STMT(self, no):
        ident = no.filhos[0]
        expr = no.filhos[1]

        nome_var = ident.valor.valor
        tipo_variavel = self.visita(ident)
        tipo_expressao = self.visita(expr)

        if not self._sao_compativeis(tipo_variavel, tipo_expressao):
            raise Exception(
                f"[Linha {ident.valor.linha}] "
                f"Erro: não pode atribuir {tipo_expressao} em {tipo_variavel}"
            )

    def visitor_BINARY_OP(self, no):
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
            raise Exception(
                f"[Linha {no.valor.linha}] "
                f"Operação inválida: {tipo_esq} {op.name} {tipo_dir}"
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
            raise Exception(
                f"[Linha {no.valor.linha}] Comparação inválida"
            )

        if op in {TokenType.AND, TokenType.OR}:
            if tipo_esq == "bool" and tipo_dir == "bool":
                return "bool"
            raise Exception(
                f"[Linha {no.valor.linha}] Operação lógica inválida"
            )

    def visitor_UNARY_OP(self, no):
        expr = no.filhos[0]
        tipo = self.visita(expr)
        op = no.valor.tipo

        if op == TokenType.NOT:
            if tipo != "bool":
                raise Exception(f"[Linha {no.valor.linha}] NOT precisa de bool")
            return "bool"

        if op in {TokenType.PLUS, TokenType.MINUS}:
            if tipo in ["int", "real"]:
                return tipo
            raise Exception(f"[Linha {no.valor.linha}] Operador inválido")


    def visitor_IF_STMT(self, no):
        cond = no.filhos[0]
        bloco_if = no.filhos[1]

        tipo_cond = self.visita(cond)

        if tipo_cond != "bool":
            raise Exception(
                f"[Linha {cond.valor.linha}] IF precisa de bool"
            )

        self.visita(bloco_if)

        if len(no.filhos) > 2:
            self.visita(no.filhos[2])

    def visitor_WHILE_STMT(self, no):
        cond = no.filhos[0]
        bloco = no.filhos[1]

        tipo_cond = self.visita(cond)

        if tipo_cond != "bool":
            raise Exception(
                f"[Linha {cond.valor.linha}] WHILE precisa de bool"
            )

        self.visita(bloco)

    def visitor_FUNCTION_DECL(self, no):
        ident = no.filhos[0]
        nome_funcao = ident.valor.valor

        tipo_node = no.filhos[-2]
        tipo_retorno = tipo_node.valor.valor

        self.scope[-1][nome_funcao] = tipo_retorno

        self.scope.append({})  

        if len(no.filhos) > 3:
            param_list = no.filhos[1]
            for param in param_list.filhos:
                nome_param = param.filhos[0].valor.valor
                tipo_param = param.filhos[1].valor.valor
                self.scope[-1][nome_param] = tipo_param

        self.visita(no.filhos[-1])

        self.scope.pop()

    def visitor_RETURN_STMT(self, no):
        expr = no.filhos[0]
        return self.visita(expr)

    def visitor_FUNCTION_CALL(self, no):
        nome = no.filhos[0].valor.valor
        tipo_func = self.visita(no.filhos[0])

        if len(no.filhos) > 1:
            for arg in no.filhos[1].filhos:
                self.visita(arg)

        return tipo_func

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

    def _sao_compativeis(self, tipo_alvo, tipo_dado):
        if tipo_alvo == tipo_dado:
            return True
        if tipo_alvo == "real" and tipo_dado == "int":
            return True
        return False