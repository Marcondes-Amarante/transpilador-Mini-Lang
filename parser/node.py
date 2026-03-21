class Node:
    def __init__(self, valor: str, tipo: str) -> None:
        self.__tipo: str = tipo
        self.__valor: str = valor
        self.__filhos: list["Node"] = []

    @property
    def tipo(self) -> str:
        return self.__tipo

    @property
    def valor(self) -> str:
        return self.__valor

    @property
    def filhos(self) -> tuple["Node"]:
        return tuple(self.__filhos)

    def add_filho(self, filho: "Node") -> None:
        self.__filhos.append(filho)
