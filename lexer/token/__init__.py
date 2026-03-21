from .token import Token, TokenType
from .translators import ARITHMETIC_OPERATORS, DELIMITERS, RESERVED_KEYWORDS

TOKEN_MAP = {
    **RESERVED_KEYWORDS,
    **ARITHMETIC_OPERATORS,
    **DELIMITERS,
}

__all__ = [
    "Token",
    "TokenType",
    "ARITHMETIC_OPERATORS",
    "DELIMITERS",
    "RESERVED_KEYWORDS",
    "TOKEN_MAP",
]
