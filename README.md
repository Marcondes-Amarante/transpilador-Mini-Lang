# Projeto compiladores: transpilador mini-lang

O presente projeto foi desenvolvido sobre intuito de consolidar conhecimentos teóricos obtidos durante a disciplina de compiladores ofertada pelo docente Laszlon Rodrigues da Costa no período 2025.2, e consiste em um transpilador (compilador fonte-para-fonte) de mini lang. A mini lang é uma linguagem imperativa, procedural, e estaticamente tipada projetada para fins didáticos. 

O transpilador em questão recebe um arquivo .txt contendo o código fonte em mini lang e o traduz automaticamente para a linguagem de alto nível C, passando por todas as fases de análise e processamento, com execeção da geração da representação intermediária (aqui substituída pela geração do código final), compreendidas pela etapa de front-end de um compilador convencional. 

## 📖 Estrutura gramatical

O transpilador utilizou a seguinte estrutura gramatical EBNF disponibilizada como referência:

```ebnf
<program> ::= { <statement> }

<block> ::= "{" { <statement> } "}"

<statement> ::= <variable_decl> ";"
              | <assignment> ";"
              | <print_statement> ";"
              | <if_statement>
              | <while_statement>
              | <return_statement> ";"
              | <function_decl>
              | <block>

<function_decl> ::= "def" <identifier> "(" [<formal_params>] ")" ":" <type> <block>

<formal_params> ::= <formal_param> { "," <formal_param> }
<formal_param> ::= <identifier> ":" <type>

<while_statement> ::= "while" "(" <expression> ")" <block>
<if_statement> ::= "if" "(" <expression> ")" <block> ["else" <block>]

<return_statement> ::= "return" <expression>
<print_statement> ::= "print" <string_literal>

<type> ::= "int" | "real" | "bool" | "void"

<variable_decl> ::= "var" <identifier> ":" <type> "=" <expression>
<assignment> ::= "set" <identifier> "=" <expression>

<expression> ::= <simple_expression> { <relational_op> <simple_expression> }
<simple_expression> ::= <term> { <additive_op> <term> }
<term> ::= <factor> { <multiplicative_op> <factor> }

<factor> ::= <literal>
           | <identifier>
           | <function_call>
           | <sub_expression>
           | <unary>

<unary> ::= ("+" | "-" | "not") { <expression> }

<sub_expression> ::= "(" <expression> ")"

<function_call> ::= <identifier> "(" [<actual_params>] ")"
<actual_params> ::= <expression> { "," <expression> }

<relational_op> ::= "<" | ">" | "==" | "!=" | "<=" | ">="
<additive_op> ::= "+" | "-" | "or"
<multiplicative_op> ::= "*" | "/" | "and"

<identifier> ::= ("_" | <letter>) { "_" | <letter> | <digit> }
<digit> ::= [0-9]
<letter> ::= [a-zA-Z]

<literal> ::= <integer_literal> | <real_literal> | "true" | "false"
<integer_literal> ::= [0-9]+
<real_literal> ::= [0-9]+ "." [0-9]+

<string_literal> ::= '"' {<letter> | <digit> | <symbol> | " "} '"'
< symbol > ::= <any - char - except - quote > ( Qualquer caractere imprimivel , exceto aspas )
```

A fim de garantir a correta análise e geração da AST, efetuamos modificações pontuais nas regraa do `print_statement`, que modificamos para `print-statement = "print" (string_literal | expression) ;`, e do `unary`, que modificamos para `unary = ("+"|"-"|"not") unary | factor` 

## 📐 Arquitetura

O transpilador segue a estrutura clássica da etapa de front-end de compiladores convencionais:

1. Analisador léxico (`lexer.py`): quebra e estrutura as sequências de caracteres do código fonte mini-lang em tokens, que guardam informações como tipo, valor e linha de referência.

2. Analisador sintático (`parser.py`): analisa a ordem dos tokens mapeando sua estrutura em uma Árvore Sintática Abstrata (AST) composta por Nós, que armazenam informações de tipo, o próprio token, e uma lista de filhos.

3. Analisador semântico (`semantic.py`): analisa o sentido lógico da árvore sintática amparado pela consulta e construção de uma tabela de símbolos distribuídos por escopos, validando a estrutura de acordo com aspectos como declaração prévia de variáveis, inexistência de duplicidade de declarações e compatibilidade de tipos. 

4. gerador de código final (`C_generator.py`): percorre a AST previamente validada gerando trechos de código C válidos para cada nó visitado, resultando em um arquivo de código `.c` pronto para ser compilado por um compilador comercial.

5. `main.py`: agrupa a chamada de instâncias de todas as etapas anteriores de maneira ordenada, e gerencia a criação do arquivo final e artefatos intermediários (listagem de tokens e json da AST validada)

```
código Mini-Lang ──► Léxico ──► Sintático ──► Semântico ──► gerador de código ──► código final em C
```

## 🚀 Instruções de execução

### 1. Crie um arquivo `.txt` contendo o código mini-lang que deseja compilar

### 2. Em um terminal, estando na pasta raiz do projeto, execute a seguinte instrução:

```
python main.py codigo.txt -save -print 
```
onde:

- `codigo.txt`: refere-se ao caminho relativo do codigo fonte mini-lang previamente criado, recomendamos armazená-lo na pasta 'testes para fins de melhor organização.
- `-save`: é um parâmetro opicional que cria uma pasta chamada 'artifacts', onde será armazenado um arquivo .txt da lista de tokens, um arquivo .json da AST gerada, e um arquivo .c referente ao código final gerado.
- `-print`: é um parâmetro permite a exibição da lista de tokens e da AST no terminal durante a execução.

### 3. digite o número da opção desejada dentre as exibidas no terminal:

```
Deseja gerar o equivalente do código em C?
1. Printar e salvar
2. Apenas printar
3. Apenas salvar
4. Não
```

sendo `printar` para exibir o código gerado no terminal, e `salvar` para gerar o arquivo .c