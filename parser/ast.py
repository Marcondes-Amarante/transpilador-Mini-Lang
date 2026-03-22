from .node import Node
import json


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

    def save_tree(self, path: str) -> None:
        try:
            ast_dict = self.__node_to_dict(self.raiz)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(ast_dict, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar AST: {e}")

    def __node_to_dict(self, node: Node) -> dict:
        if node is None:
            return None
        return {
            "tipo": node.tipo,
            "valor": node.valor.to_dict() if node.valor else None,
            "filhos": [self.__node_to_dict(filho) for filho in node.filhos],
        }
