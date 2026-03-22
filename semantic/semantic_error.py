class SemanticError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"[Erro de Semântica] {message} na linha {line}")
