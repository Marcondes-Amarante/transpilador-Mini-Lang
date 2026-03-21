class LexicalError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"[Erro Lexical] {message} na linha {line}")
