import json
import logging

from src.adapters.llm.client import OllamaClient
from src.domain.entities import Item, Tag
from src.domain.enums import Sentiment, Urgency
from src.domain.exceptions import LLMParseError
from src.domain.interfaces import ITagger

logger = logging.getLogger(__name__)

TAGGING_PROMPT = """Ты — система классификации отзывов и вопросов с маркетплейсов.

Проанализируй текст и верни ТОЛЬКО JSON без дополнительного текста:
{{
  "sentiment": "positive" | "negative" | "neutral",
  "topic": "<одно слово на русском: качество, доставка, упаковка, размер, цена, брак, комплектация, описание, другое>",
  "urgency": "low" | "medium" | "high",
  "requires_response": true | false
}}

Правила:
- Для вопросов requires_response всегда true
- Для положительных отзывов без конкретной проблемы — requires_response: true (благодарим)
- Для отзывов с 1-2 звёздами urgency: high
- Для отзывов с 3 звёздами urgency: medium

Тип: {item_type}
Оценка: {rating}
Текст: {text}

/nothink
"""


class OllamaTagger(ITagger):
    def __init__(self, client: OllamaClient, model: str) -> None:
        self._client = client
        self._model = model

    def tag(self, item: Item) -> Tag:
        prompt = TAGGING_PROMPT.format(
            item_type="отзыв" if item.item_type.value == "review" else "вопрос",
            rating=item.rating if item.rating else "нет оценки",
            text=item.text[:2000],
        )

        raw = self._client.generate(self._model, prompt, timeout=120.0)
        parsed = self._parse_response(raw)

        return Tag(
            item_id=item.id,
            sentiment=parsed.get("sentiment"),
            topic=parsed.get("topic"),
            urgency=parsed.get("urgency", Urgency.LOW),
            requires_response=parsed.get("requires_response", True),
            model_name=self._model,
        )

    def _parse_response(self, raw: str) -> dict:
        try:
            text = raw.strip()
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                text = text[start:end]
            data = json.loads(text)

            result = {}
            if "sentiment" in data and data["sentiment"] in ("positive", "negative", "neutral"):
                result["sentiment"] = Sentiment(data["sentiment"])
            if "topic" in data:
                result["topic"] = str(data["topic"])[:100]
            if "urgency" in data and data["urgency"] in ("low", "medium", "high"):
                result["urgency"] = Urgency(data["urgency"])
            if "requires_response" in data:
                result["requires_response"] = bool(data["requires_response"])

            return result
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise LLMParseError(f"Failed to parse tagger response: {e}. Raw: {raw[:500]}") from e
