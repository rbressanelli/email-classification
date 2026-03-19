from __future__ import annotations

from typing import Optional

from openai import OpenAI

from app.core.config import settings
from app.services.classifier import ClassificationResult


class ReplyGenerator:
    def __init__(self) -> None:
        self.client: Optional[OpenAI] = None
        if settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)

    @property
    def provider_name(self) -> str:
        return "OpenAI" if self.client else "Local template"

    def generate(self, original_text: str, result: ClassificationResult) -> str:
        if self.client:
            try:
                return self._generate_with_llm(original_text, result)
            except Exception:
                return self._generate_template(result)
        return self._generate_template(result)

    def _generate_with_llm(
        self, original_text: str, result: ClassificationResult
    ) -> str:
        completion = self.client.responses.create(  # type: ignore
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente de operações de uma empresa financeira. "
                        "Responda em português do Brasil, com tom profissional, objetivo e cordial. "
                        "Se a classe for Improdutivo, agradeça e encerre sem prometer ação. "
                        "Se a classe for Produtivo, confirme recebimento e indique próximos passos plausíveis."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Classificação: {result.label}\n"
                        f"Resumo: {result.summary}\n"
                        f"Email original:\n{original_text}\n\n"
                        "Gere uma sugestão de resposta curta, pronta para uso."
                    ),
                },
            ],
        )
        return completion.output_text.strip()

    def _generate_template(self, result: ClassificationResult) -> str:
        if result.label == "Produtivo":
            return (
                "Olá! Recebemos sua mensagem e registramos a solicitação. "
                "Nossa equipe irá analisar o caso e retornar com uma atualização ou próximos passos o quanto antes. "
                "Caso exista algum documento complementar, por favor, mantenha-o disponível para agilizar o atendimento."
            )
        return (
            "Olá! Agradecemos sua mensagem e o contato com a nossa equipe. "
            "Registramos o conteúdo recebido e, no momento, não há nenhuma ação adicional necessária da nossa parte. "
            "Seguimos à disposição caso surja alguma demanda futura."
        )
