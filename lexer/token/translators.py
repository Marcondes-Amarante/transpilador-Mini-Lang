from .token_type import TokenType

DELIMITERS: dict[str, TokenType] = {
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    ":": TokenType.COLON,
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
}

RESERVED_KEYWORDS: dict[str, TokenType] = {
    "def": TokenType.DEF,
    "while": TokenType.WHILE,
    "if": TokenType.IF,
    "return": TokenType.RETURN,
    "print": TokenType.PRINT,
    "int": TokenType.INT_TYPE,
    "real": TokenType.REAL_TYPE,
    "bool": TokenType.BOOL_TYPE,
    "void": TokenType.VOID_TYPE,
    "var": TokenType.VAR,
    "set": TokenType.SET,
    "not": TokenType.NOT,
    "or": TokenType.OR,
    "and": TokenType.AND,
    "true": TokenType.BOOLEAN_LITERAL,
    "false": TokenType.BOOLEAN_LITERAL,
}

ARITHMETIC_OPERATORS: dict[str, TokenType] = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MULTIPLY,
    "/": TokenType.DIVIDE,
}