from .node_type import NodeType
from lexer import Token

class Node:
    def __init__(self, tipo: NodeType ) -> None:
        self.__tipo: NodeType = tipo
        self.__valor: Token | None = None
        self.__filhos: list["Node"] = []

    @property
    def tipo(self) -> NodeType:
        return self.__tipo

    @property
    def valor(self) -> Token | None:
        return self.__valor
    
    @valor.setter
    def valor(self, valor: Token) -> None:
        self.__valor = valor

    @property
    def filhos(self) -> tuple["Node"]:
        return tuple(self.__filhos)
    
    def __str__(self):
        return f"<{self.__tipo.name}, {self.__valor}>"

    def add_filho(self, filho: "Node") -> None:
        self.__filhos.append(filho)
        

