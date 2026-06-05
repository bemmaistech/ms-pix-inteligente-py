import re
from typing import List


class TextoTratamento:
    """Classe para tratar texto extraído por OCR e retornar lista de linhas limpas."""

    def __init__(self, texto: str):
        self.texto = texto or ""

    def process(self) -> List[str]:
        """Retorna a lista tratada conforme a regra de negócio."""
        linhas = self._split_lines(self.texto)
        linhas = [self._normalize_line(linha) for linha in linhas]
        linhas = [linha for linha in linhas if self._is_valid_line(linha)]
        return linhas

    def _split_lines(self, texto: str) -> List[str]:
        return texto.splitlines()

    def _normalize_line(self, linha: str) -> str:
        linha = linha.strip()
        linha = re.sub(r"\s+", " ", linha)
        return linha

    def _is_valid_line(self, linha: str) -> bool:
        if not linha:
            return False
        if len(linha) < 2:
            return False
        if re.fullmatch(r"[\W_]+", linha):
            return False
        return True


if __name__ == "__main__":
    exemplo = "  Linha 1\n\nLinha 2  \n---\n   \nLinha 3"
    tratamento = TextoTratamento(exemplo)
    linhas = tratamento.process()
    print(linhas)
