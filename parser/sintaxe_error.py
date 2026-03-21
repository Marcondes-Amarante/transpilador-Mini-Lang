class MiniLangSyntaxError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"[Erro de Sintaxe] {message} na linha {line}")
