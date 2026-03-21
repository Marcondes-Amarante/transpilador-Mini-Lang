from .node import Node
from typing import Optional

class AST:
    def __init__(self) -> None:
        self.__raiz: Optional[Node] = None

    @property
    def raiz(self) -> Node:
        if (self.__raiz is None):
            raise Exception("AST: raiz não inicializada")
        return self.__raiz
