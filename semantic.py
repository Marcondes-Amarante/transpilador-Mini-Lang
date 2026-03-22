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
        if nome_var not in self.tabela_simbolos:
            raise Exception(f"Erro Semântico (Linha {no.valor.linha}): Variável '{nome_var}' não declarada.")
        return self.tabela_simbolos[nome_var]


    def visitor_VAR_DECL(self, no):
        nome_var = no.filhos.valor.valor
        tipo_declarado = no.filhos.valor.valor 
        tipo_expressao = self.visita(no.filhos)

        if not self._sao_compativeis(tipo_declarado, tipo_expressao):
            raise Exception(f"Erro Semântico (Linha {no.filhos.valor.linha}): "
                            f"Tentando inicializar '{nome_var}' ({tipo_declarado}) com {tipo_expressao}.")

        self.tabela_simbolos[nome_var] = tipo_declarado

    def visitor_ASSIGN_STMT(self, no):
        nome_var = no.filhos.valor.valor
        tipo_variavel = self.visitor_IDENTIFIER(no.filhos)
        tipo_expressao = self.visita(no.filhos)

        if not self._sao_compativeis(tipo_variavel, tipo_expressao):
            raise Exception(f"Erro Semântico (Linha {no.filhos.valor.linha}): "
                            f"Não é possível atribuir {tipo_expressao} à variável '{nome_var}' ({tipo_variavel}).")


    def visitor_BINARY_OP(self, no):
        tipo_esq = self.visita(no.filhos)
        tipo_dir = self.visita(no.filhos)
        op_token = no.valor.tipo

        if op_token in {TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE}:
            if tipo_esq == "int" and tipo_dir == "int":
                return "int"
            if tipo_esq in ["int", "real"] and tipo_dir in ["int", "real"]:
                return "real"
            raise Exception(f"Erro (Linha {no.valor.linha}): Operação aritmética inválida entre {tipo_esq} e {tipo_dir}.")

        if op_token in {TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS, TokenType.GREATER, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL}:
            if tipo_esq == tipo_dir or (tipo_esq in ["int", "real"] and tipo_dir in ["int", "real"]):
                return "bool"
            raise Exception(f"Erro (Linha {no.valor.linha}): Comparação inválida entre {tipo_esq} e {tipo_dir}.")

        if op_token in {TokenType.AND, TokenType.OR}:
            if tipo_esq == "bool" and tipo_dir == "bool":
                return "bool"
            raise Exception(f"Erro (Linha {no.valor.linha}): Operadores lógicos exigem booleanos.")


    def _sao_compativeis(self, tipo_alvo, tipo_dado):
        if tipo_alvo == tipo_dado:
            return True
        if tipo_alvo == "real" and tipo_dado == "int":
            return True
        return False