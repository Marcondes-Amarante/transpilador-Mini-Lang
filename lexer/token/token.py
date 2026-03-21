from .token_type import TokenType

class Token:
    def __init__(self, tipo: TokenType, valor: str, linha: int):
        self.__tipo: TokenType = tipo
        self.__valor: str = valor
        self.__linha: int = linha

    @property
    def tipo(self) -> TokenType:
        return self.__tipo

    @property
    def valor(self) -> str:
        return self.__valor

    @property
    def linha(self) -> int:
        return self.__linha

    def __repr__(self) -> str:
        return f"Token({self.__tipo}, {self.__valor}, {self.__linha})"

    def __str__(self) -> str:
        return f"<{self.__tipo.name}, {self.__valor}>"
