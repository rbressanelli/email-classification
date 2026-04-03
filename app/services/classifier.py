import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.services.preprocessor import preprocess_text, normalize_text

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "training_data.json"


def load_training_data() -> List[Tuple[str, int]]:
    if not DATA_PATH.exists():
        return [
            ("E-mail de exemplo produtivo", 1),
            ("E-mail de exemplo improdutivo", 0),
        ]

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    combined = []
    for text in data.get("productive", []):
        combined.append((text, 1))
    for text in data.get("unproductive", []):
        combined.append((text, 0))
    for text in data.get("invalid", []):
        combined.append((text, 0))

    return combined


PRODUCTIVE_KEYWORDS = {
    "status",
    "solicitação",
    "solicitacao",
    "erro",
    "problema",
    "anexo",
    "anex",
    "anális",
    "analise",
    "caso",
    "requisição",
    "requisicao",
    "suporte",
    "ajuda",
    "documento",
    "prazo",
    "retorno",
    "portal",
    "acesso",
    "chamado",
    "ticket",
    "atualização",
    "atualizacao",
    "urgente",
    "boleto",
    "fatura",
    "relatório",
    "instabilidade",
    "servidor",
    "manual",
    "integração",
    "atendimento",
    "atraso",
    "validação",
    "validacao",
    "contrato",
    "segunda via",
    "agendar",
    "reunião",
    "reuniao",
    "cancelar",
    "assinatura",
    "link",
    "teste",
    "confirmar",
    "catálogo",
    "catalogo",
    "premium",
    "reembolso",
    "pagamento",
    "pendente",
    "atualizar",
    "dados",
    "chamada",
    "entrega",
    "troca",
    "fiscal",
    "nf",
    "parcelamento",
    "mobile",
    "lentidão",
    "lentidao",
    "autenticação",
    "autenticacao",
    "recuperar",
    "baixar",
    "instalador",
    "orçamento",
    "orcamento",
    "licença",
    "licenca",
    "cupom",
    "carrinho",
    "vaga",
    "webinar",
    "cartão",
    "cartao",
    "histórico",
    "historico",
    "titular",
    "segurança",
    "seguranca",
    "migração",
    "migracao",
    "perfil",
    "whatsapp",
    "demonstração",
    "demonstracao",
    "documentação",
    "documentacao",
    "excluir",
    "login",
    "python",
    "limite",
}

UNPRODUCTIVE_KEYWORDS = {
    "obrigado",
    "agradec",
    "feliz",
    "parab",
    "boas",
    "festas",
    "natal",
    "ano",
    "novo",
    "ótimo",
    "otimo",
    "sem",
    "necessidade",
    "retorno",
    "bom dia",
    "boa tarde",
    "boa noite",
    "finalizado",
    "resolvido",
    "anotado",
    "entendido",
    "show",
    "despedida",
    "aniversário",
    "aniversario",
    "indicação",
    "indicacao",
    "registro",
    "conferência",
    "conferencia",
    "esclarecido",
    "dica",
    "feriado",
    "apresentação",
    "apresentacao",
    "brinde",
    "incentivo",
    "feedback",
    "confraternização",
    "confraternizacao",
    "expediente",
    "didático",
    "recuperação",
    "recuperacao",
    "visita",
    "encerrar",
}


@dataclass
class ClassificationResult:
    label: str
    confidence: float
    reasoning: str
    detected_signals: List[str]
    summary: str
    processed_text: str


class HybridEmailClassifier:
    def __init__(self) -> None:
        training_data = load_training_data()
        texts = [preprocess_text(text) for text, _ in training_data]
        labels = [label for _, label in training_data]
        self.pipeline = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5))),
                ("clf", LogisticRegression(max_iter=1000)),
            ]
        )
        self.pipeline.fit(texts, labels)

    def classify(self, text: str) -> ClassificationResult:
        normalized = normalize_text(text)
        processed = preprocess_text(normalized)

        if self._is_gibberish(normalized) or not processed.strip():
            return ClassificationResult(
                label="Improdutivo",
                confidence=0.99,
                reasoning="O texto não parece conter linguagem natural legível ou um contexto de e-mail válido para análise.",
                detected_signals=["Sistema: Detecção de conteúdo inválido/gibberish"],
                summary="[Conteúdo Inválido]",
                processed_text=processed,
            )

        probabilities = self.pipeline.predict_proba([processed])[0]
        productive_score = float(probabilities[1])

        signals: list[str] = []
        lowered = normalized.lower()

        for keyword in PRODUCTIVE_KEYWORDS:
            if keyword in lowered:
                productive_score += 0.03
                signals.append(f"Sinal produtivo: '{keyword}'")

        for keyword in UNPRODUCTIVE_KEYWORDS:
            if keyword in lowered:
                productive_score -= 0.025
                signals.append(f"Sinal improdutivo: '{keyword}'")

        productive_score = max(0.0, min(1.0, productive_score))
        is_productive = productive_score >= 0.5
        confidence = productive_score if is_productive else 1 - productive_score
        label = "Produtivo" if is_productive else "Improdutivo"

        reasoning = (
            "O email requer uma ação, resposta ou acompanhamento operacional (expectativa de retorno)."
            if is_productive
            else "O email é informativo, social ou de encerramento, sem expectativa de resposta imediata."
        )

        summary = self._summarize(normalized)

        return ClassificationResult(
            label=label,
            confidence=round(confidence, 3),
            reasoning=reasoning,
            detected_signals=signals[:6],
            summary=summary,
            processed_text=processed,
        )

    def _is_gibberish(self, text: str) -> bool:
        """Determina se o texto parece ser aleatório ou sem sentido."""
        import re
        
        text = text.strip()
        if not text:
            return True

        if len(text) < 3:
            return True

        words = text.split()
        if not words:
            return True

        # 1. Palavras excessivamente longas sem pontuação/símbolos
        long_words = [w for w in words if len(w) >= 25 and "@" not in w and "/" not in w and "." not in w]
        if long_words:
            return True

        # 2. Proporção extrema de vogais/consoantes
        letters = "".join(filter(str.isalpha, text.lower()))
        if len(letters) > 8:
            vowels = sum(1 for char in letters if char in "aeiouáéíóúâêîôûãõàèìòù")
            ratio = vowels / len(letters)
            if ratio < 0.15 or ratio > 0.85:
                return True

        # 3. Sequência excessiva de consoantes
        if re.search(r"[bcdfghjklmnpqrstvwxyz]{7,}", text.lower()):
            return True

        return False

    @staticmethod
    def _summarize(text: str, limit: int = 180) -> str:
        text = text.strip().replace("\n", " ")
        if len(text) <= limit:
            return text
        return text[: limit - 3].rstrip() + "..."
