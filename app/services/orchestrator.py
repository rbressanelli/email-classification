from app.core.schemas import AnalysisResponse
from app.services.classifier import HybridEmailClassifier
from app.services.reply_generator import ReplyGenerator


class EmailAnalysisOrchestrator:
    def __init__(self) -> None:
        self.classifier = HybridEmailClassifier()
        self.reply_generator = ReplyGenerator()

    @property
    def provider_name(self) -> str:
        return self.reply_generator.provider_name

    def analyze(self, text: str) -> AnalysisResponse:
        result = self.classifier.classify(text)
        reply = self.reply_generator.generate(text, result)
        return AnalysisResponse(
            category=result.label, # type: ignore
            confidence=result.confidence,
            suggested_reply=reply,
            summary=result.summary,
            reasoning=result.reasoning,
            detected_signals=result.detected_signals,
            processed_text=result.processed_text,
        )
