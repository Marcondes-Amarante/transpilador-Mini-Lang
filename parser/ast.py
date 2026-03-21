from .node import Node
from typing import Optional


class AST:
    def __init__(self, raiz: Node) -> None:
        self.__raiz: Node = raiz

    @property
    def raiz(self) -> Node:
        if self.__raiz is None:
            raise Exception("AST: raiz não inicializada")
        return self.__raiz

    def print_tree(self) -> None:
        self.__print_node(self.raiz, "", True)

    def __print_node(self, node: Node, prefix: str, is_last: bool) -> None:
        if node is None:
            return

        connector = "└── " if is_last else "├── "
        print(prefix + connector + f"{node.tipo.name} ({node.valor})")

        filhos = node.filhos
        for i, filho in enumerate(filhos):
            is_last_child = i == len(filhos) - 1
            new_prefix = prefix + ("    " if is_last else "│   ")
            self.__print_node(filho, new_prefix, is_last_child)
