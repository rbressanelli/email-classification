from __future__ import annotations

from dataclasses import dataclass
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.services.preprocessor import preprocess_text, normalize_text


TRAINING_DATA = [
    (
        "Preciso de uma atualização sobre o chamado 4832, o sistema segue indisponível.",
        1,
    ),
    (
        "Poderiam verificar o erro no acesso ao portal? Não consigo entrar desde ontem.",
        1,
    ),
    ("Encaminho em anexo o contrato solicitado para continuidade da análise.", 1),
    ("Qual o status da minha requisição de alteração cadastral?", 1),
    ("Favor confirmar recebimento do documento e próximos passos.", 1),
    ("Bom dia, seguem evidências do problema identificado em produção.", 1),
    ("Gostaria de saber quando meu caso será concluído.", 1),
    (
        "O arquivo enviado anteriormente estava corrompido; envio novamente para validação.",
        1,
    ),
    ("Obrigado pelo apoio de ontem, excelente trabalho da equipe.", 0),
    ("Feliz Natal para todos do time.", 0),
    ("Somente passando para agradecer a ajuda prestada.", 0),
    ("Parabéns pelo novo sistema, ficou muito bom.", 0),
    ("Boa tarde, tudo certo por aí?", 0),
    ("Agradeço pela atenção e desejo um ótimo final de semana.", 0),
    ("Mensagem de teste sem necessidade de retorno.", 0),
    ("Boas festas e um próspero ano novo.", 0),
]

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
    "teste",
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
        texts = [preprocess_text(text) for text, _ in TRAINING_DATA]
        labels = [label for _, label in TRAINING_DATA]
        self.pipeline = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
                ("clf", LogisticRegression(max_iter=1000)),
            ]
        )
        self.pipeline.fit(texts, labels)

    def classify(self, text: str) -> ClassificationResult:
        normalized = normalize_text(text)
        processed = preprocess_text(normalized)
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
            "O email contém pedido de ação, acompanhamento ou compartilhamento de informação útil."
            if is_productive
            else "O email tem caráter social, cordial ou informativo sem demanda operacional imediata."
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

    @staticmethod
    def _summarize(text: str, limit: int = 180) -> str:
        text = text.strip().replace("\n", " ")
        if len(text) <= limit:
            return text
        return text[: limit - 3].rstrip() + "..."
