import re
from typing import List, Dict, Optional


KNOWN_BANKS = [
    "Banco do Brasil",
    "Bradesco",
    "Itaú",
    "Itaú Unibanco",
    "Caixa",
    "Santander",
    "Nubank",
    "Inter",
    "Sicredi",
    "Original",
]


MONTH_ABBREVS = {
    "jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez",
    "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
}


class SeparadorDados:
    """Classe para separar dados de uma lista de texto e retornar um dicionário."""

    def __init__(self, lista: List[str]):
        self.lista = lista

    def processar(self) -> Dict[str, Optional[str]]:
        """Recebe a lista e retorna o dicionário com banco, hora, recebedor e valor.

        Nota: o campo `recebedor` representa o nome extraído do comprovante; quando
        for possível identificar o pagador (quem fez a transação), esse nome será
        usado para o campo (atendimento ao pedido do usuário).
        """
        if len(self.lista) == 1:
            tokens = re.split(r"[\n\r]+|[;,]\s*|\s{2,}", self.lista[0])
        else:
            tokens = self.lista

        texto = " ".join(tokens)
        banco = self._encontrar_banco(tokens)
        hora = self._encontrar_hora(texto)
        valor = self._encontrar_valor(texto)
        pagador = self._encontrar_pagador(tokens, banco, hora, valor)
        recebedor = pagador or self._encontrar_recebedor(tokens, banco, hora, valor)

        return {"banco": banco, "hora": hora, "recebedor": recebedor, "valor": valor}

    def _encontrar_banco(self, tokens: List[str]) -> Optional[str]:
        text = " ".join(tokens)
        for banco in KNOWN_BANKS:
            if banco.lower() in text.lower():
                return banco
        # procura por palavra 'banco' seguida de nome
        m = re.search(r"banco\s+([A-Za-z0-9]+)", text, re.IGNORECASE)
        if m:
            return m.group(0)
        return None

    def _encontrar_hora(self, texto: str) -> Optional[str]:
        m = re.search(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", texto)
        if m:
            return m.group(0)
        # alternativa com h ou H
        m = re.search(r"\b(?:[01]?\d|2[0-3])h[0-5]\d\b", texto, re.IGNORECASE)
        if m:
            return m.group(0)
        return None

    def _encontrar_valor(self, texto: str) -> Optional[str]:
        # padrões como R$ 1.234,56 ou 1234.56 ou 1234,56
        m = re.search(r"R\$\s?[0-9\.,]+", texto)
        if m:
            return self._normalizar_valor(m.group(0))
        m = re.search(r"\b[0-9]{1,3}(?:[\.,][0-9]{3})*(?:[\.,][0-9]{2})\b", texto)
        if m:
            return self._normalizar_valor(m.group(0))
        return None

    def _normalizar_valor(self, valor: str) -> str:
        """Remove símbolos e espaços desnecessários do valor."""
        return valor.replace("R$", "").strip()

    def _is_valid_name(self, s: str) -> bool:
        if not s or len(s) < 3:
            return False
        words = [w for w in re.split(r"\s+", s) if w]
        if len(words) < 2:
            return False
        if any(len(re.sub(r"[^A-Za-zÀ-ÿ]", "", w)) < 2 for w in words):
            return False
        lower = s.strip().lower()
        if lower in MONTH_ABBREVS:
            return False
        return True

    def _encontrar_pagador(
        self,
        tokens: List[str],
        banco: Optional[str],
        hora: Optional[str],
        valor: Optional[str],
    ) -> Optional[str]:
        """Tenta identificar quem fez a transação (pagador/remetente).

        Procura por padrões explícitos como 'DE:', 'ORIGEM:', 'REMETENTE:',
        ou frases como 'QUE FEZ A TRANSACAO <nome>' / 'QUEM FEZ O PIX <nome>'.
        """
        lower_tokens = [t.lower() for t in tokens]
        full_text = " ".join(tokens)

        # 0a) Captura explícita do bloco 'Dados de quem fez' seguido por 'Nome' e o nome na próxima linha
        for i, lt in enumerate(lower_tokens):
            if "dados de quem fez" in lt or "dados de quem fez a" in lt or ("dados de quem" in lt and "fez" in lt):
                # procurar próximos tokens para localizar a linha 'Nome' e o nome em seguida
                for j in range(1, 6):
                    if i + j >= len(tokens):
                        break
                    cand = tokens[i + j].strip()
                    if not cand:
                        continue
                    # se a linha for 'Nome', tente a próxima linha como nome
                    if cand.lower().startswith("nome"):
                        if i + j + 1 < len(tokens):
                            candidate = tokens[i + j + 1].strip()
                        else:
                            candidate = ""
                    else:
                        candidate = cand
                    name = self._extrair_nome_de_linha(candidate)
                    if name and self._is_valid_name(name):
                        return name

        # Verifica tokens que contenham frases como 'que fez', 'quem fez' seguido do nome
        for token in tokens:
            lt = token.lower()
            for phrase in ("que fez a transacao", "que fez a transação", "quem fez o pix", "quem fez o pix", "quem fez", "quem enviou", "quem efetuou", "quem realizou"):
                if phrase in lt:
                    start = lt.find(phrase) + len(phrase)
                    candidate = token[start:].strip(" :,-\t")
                    name = self._extrair_nome_de_linha(candidate)
                    if name and self._is_valid_name(name):
                        return name

        # 0) Busca em todo o texto por frases que indiquem o remetente/pagador
        m = re.search(
            r"(?:quem (?:fez|enviou|efetuou|realizou)(?: a| o)?(?: transac(?:ç|c)ao|transfer(?:ê|e)ncia|pix)[\s:,-]+|que fez(?: a| o)?(?: transac(?:ç|c)ao|transfer(?:ê|e)ncia)?[\s:,-]+)([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s]+)",
            full_text,
            re.IGNORECASE,
        )
        if m:
            candidate = m.group(1).strip()
            name = self._extrair_nome_de_linha(candidate)
            if name and self._is_valid_name(name):
                return name

        # 0b) Padrões 'DE:' ou 'DE ' seguidos do nome no texto completo
        m2 = re.search(r"\bde[:\s-]+([A-ZÀ-Ÿ][A-Za-zÀ-ÿ\s]+)", full_text, re.IGNORECASE)
        if m2:
            candidate = m2.group(1).strip()
            name = self._extrair_nome_de_linha(candidate)
            if name and self._is_valid_name(name):
                return name

        # 1) Procura por labels explícitas de remetente/pagador por linha/token
        for i, token in enumerate(tokens):
            m = re.search(
                r"^(?:de|origem|origem nome|remetente|pagador|envio(?: de)?|nome do remetente)\b[:\s-]*(.*)$",
                token,
                re.IGNORECASE,
            )
            if m:
                candidate = m.group(1).strip()
                if candidate:
                    name = self._extrair_nome_de_linha(candidate)
                    if name and self._is_valid_name(name):
                        return name
                for j in range(1, 4):
                    if i + j < len(tokens):
                        candidate = tokens[i + j].strip()
                        name = self._extrair_nome_de_linha(candidate)
                        if name and self._is_valid_name(name):
                            return name

        # 2) Se não encontrar label explícita, pega o primeiro nome válido antes do destino/para
        cutoff = len(tokens)
        for label in (
            "para",
            "destino",
            "destino nome",
            "favorecido",
            "beneficiário",
            "beneficiario",
            "recebedor",
            "destinatario",
        ):
            if label in lower_tokens:
                index = lower_tokens.index(label)
                if index < cutoff:
                    cutoff = index

        for token in tokens[:cutoff]:
            name = self._extrair_nome_de_linha(token)
            if name and self._is_valid_name(name):
                return name

        return None

    def _encontrar_recebedor(
        self,
        tokens: List[str],
        banco: Optional[str],
        hora: Optional[str],
        valor: Optional[str],
    ) -> Optional[str]:
        text = " ".join(tokens)
        for part in filter(None, [banco, hora, valor]):
            text = re.sub(re.escape(part), "", text, flags=re.IGNORECASE)

        text = re.sub(
            r"\b(?:pix(?: recebido)?|comprovante|transfer(?:ê|e)ncia|pagamento|recebido|enviado|destino nome|destino|origem nome|origem|nome|destinatario|destinatário|favorecido|favorecida|beneficiário|beneficiario|para)\b",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\s{2,}", " ", text).strip()

        if not text:
            return None

        def valid_name(s: str) -> bool:
            return self._is_valid_name(s)

        # 1) Procura por labels e pega a próxima linha útil (ex: 'Dados do recebedor' -> próxima linha)
        lower_tokens = [t.lower() for t in tokens]
        receiver_labels = (
            "destino",
            "nome",
            "dados do recebedor",
            "dados do recebimento",
            "dados do beneficiario",
            "dados do favorecido",
            "para",
            "recebedor",
            "destinatario",
            "destinatário",
        )
        for i, lt in enumerate(lower_tokens):
            for label in receiver_labels:
                if lt == label or lt.startswith(label + " ") or lt.startswith(label + ":"):
                    token = tokens[i]
                    m = re.search(rf"^{re.escape(label)}[:\s-]+(.+)$", token, re.IGNORECASE)
                    if m:
                        cand = m.group(1).strip()
                        name = self._extrair_nome_de_linha(cand)
                        if name and valid_name(name):
                            return name

                    # buscar até 3 linhas à frente para encontrar um nome
                    for j in range(1, 4):
                        if i + j < len(tokens):
                            cand = tokens[i + j].strip()
                            name = self._extrair_nome_de_linha(cand)
                            if name and valid_name(name):
                                return name

        # 1a) Prefer explicit markers: linhas que começam com 'Nome '
        for t in tokens:
            if t.lower().startswith("nome "):
                cand = t.split(None, 1)[1].strip() if len(t.split()) > 1 else ""
                name = self._extrair_nome_de_linha(cand)
                if name and valid_name(name):
                    return name

        # 1b) 'Destino' seguido por 'Nome ...' ou linha com o nome
        for i, lt in enumerate(lower_tokens):
            if lt == "destino":
                # procurar próximo token com nome
                for j in range(1, 4):
                    if i + j < len(tokens):
                        cand_line = tokens[i + j]
                        # se a linha começa com 'Nome', remova o prefixo
                        if cand_line.lower().startswith("nome "):
                            cand2 = cand_line.split(None, 1)[1].strip() if len(cand_line.split()) > 1 else ""
                        else:
                            cand2 = cand_line
                        name = self._extrair_nome_de_linha(cand2)
                        if name and valid_name(name):
                            return name

        # varredura genérica por tokens para capturar linhas que contenham 'Nome ...' ou nomes isolados
        for t in tokens:
            name = self._extrair_nome_de_linha(t)
            if name and valid_name(name):
                return name

        for t in tokens:
            m = re.search(r"(?:\d[\d\s\-\.\/]+)\s*([A-ZÀ-Ÿ][A-ZÀ-Ÿ\s]+)", t)
            if m:
                candidate = m.group(1).strip()
                candidate = re.sub(r"\s{2,}", " ", candidate)
                if valid_name(candidate):
                    return candidate

        # 3) Procura por nomes capitalizados (Ex: 'Dener Michel')
        m = re.search(r"([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)+)", text)
        if m:
            candidate = m.group(0).strip()
            if valid_name(candidate):
                return candidate

        # 4) Procura por sequências de palavras em MAIÚSCULAS com pelo menos duas palavras
        m = re.search(r"([A-ZÀ-Ÿ]{2,}(?:\s+[A-ZÀ-Ÿ]{2,})+)", text)
        if m:
            candidate = m.group(0).strip()
            if valid_name(candidate):
                return candidate

        return None

    def _extrair_nome_de_linha(self, linha: str) -> Optional[str]:
        """Tenta extrair um nome de uma linha, suportando MAIÚSCULAS e formato normal."""
        if not linha:
            return None
        # remover CNPJ/CPF padrões comuns e números
        s = re.sub(r"\b(?:CPF|CNPJ)\b[:\s]*[\d\*\./\-\s]+", "", linha, flags=re.IGNORECASE)
        s = re.sub(r"[\d\*\./\-]{2,}", "", s).strip()
        if not s:
            return None
        # se estiver todo em maiúsculas e tiver pelo menos duas palavras, retorna
        if re.fullmatch(r"[A-ZÀ-Ÿ\s]+", s) and len(s.split()) >= 2:
            return re.sub(r"\s{2,}", " ", s).strip()
        # se for capitalizado normal
        m = re.search(r"([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)+)", s)
        if m:
            return m.group(0).strip()
        return None


def separar_dados(lista: List[str]) -> Dict[str, Optional[str]]:
    """Função compatível que usa a mesma lógica da classe SeparadorDados."""
    return SeparadorDados(lista).processar()


if __name__ == "__main__":
    # exemplo rápido
    exemplo = [
        "Pix recebido",
        "Nubank",
        "Maria das Dores",
        "R$ 250,00",
        "09:15",
    ]
    print(SeparadorDados(exemplo).processar())
