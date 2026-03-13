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
