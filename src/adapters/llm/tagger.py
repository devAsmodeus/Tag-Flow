import json
import logging

from src.adapters.llm.client import OllamaClient
from src.domain.entities import Item, Tag
from src.domain.enums import Emotion, Intent, Responsibility, ResponseTone, Sentiment, Urgency
from src.domain.exceptions import LLMParseError
from src.domain.interfaces import ITagger

logger = logging.getLogger(__name__)

TAGGING_PROMPT = """Ты — система классификации отзывов и вопросов с маркетплейсов.

Проанализируй текст и верни ТОЛЬКО JSON без дополнительного текста:
{{
  "sentiment": "positive" | "negative" | "neutral",
  "topic": "<одно слово: качество, доставка, упаковка, размер, цена, брак, комплектация, описание, другое>",
  "subtopic": "<краткое описание конкретной проблемы/похвалы, 3-7 слов>",
  "emotion": "anger" | "disappointment" | "frustration" | "surprise" | "gratitude" | "indifference",
  "product_issue": "<конкретная проблема с товаром, 3-7 слов, или null если нет проблемы>",
  "intent": "return" | "exchange" | "complaint" | "info" | "gratitude",
  "keywords": ["<ключевое слово 1>", "<ключевое слово 2>", "..."],
  "urgency": "low" | "medium" | "high",
  "requires_response": true | false,
  "response_tone": "apology" | "gratitude" | "clarification" | "informational",
  "responsibility": "seller" | "marketplace" | "both" | "none"
}}

Правила:
- Для вопросов: requires_response=true, intent="info"
- Для положительных отзывов без проблемы: requires_response=true, intent="gratitude", response_tone="gratitude"
- Для отзывов с 1-2 звёздами: urgency="high"
- Для отзывов с 3 звёздами: urgency="medium"
- keywords: 3-5 самых важных слов из текста
- product_issue: null если покупатель не описывает проблему с товаром
- subtopic: конкретизация topic (например topic="качество", subtopic="термос не держит тепло")
- responsibility: кто виноват в проблеме:
  - "seller" — качество товара, комплектация, брак, описание, упаковка товара
  - "marketplace" — доставка, работа ПВЗ, поведение сотрудников ПВЗ, повреждения при транспортировке
  - "both" — и продавец и маркетплейс
  - "none" — положительный отзыв, нет проблемы

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
            subtopic=parsed.get("subtopic"),
            emotion=parsed.get("emotion"),
            product_issue=parsed.get("product_issue"),
            intent=parsed.get("intent"),
            keywords=parsed.get("keywords"),
            response_tone=parsed.get("response_tone"),
            responsibility=parsed.get("responsibility"),
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
            if "subtopic" in data and data["subtopic"]:
                result["subtopic"] = str(data["subtopic"])[:200]
            if "emotion" in data:
                try:
                    result["emotion"] = Emotion(data["emotion"])
                except ValueError:
                    pass
            if "product_issue" in data and data["product_issue"]:
                result["product_issue"] = str(data["product_issue"])[:200]
            if "intent" in data:
                try:
                    result["intent"] = Intent(data["intent"])
                except ValueError:
                    pass
            if "keywords" in data and isinstance(data["keywords"], list):
                result["keywords"] = [str(k)[:50] for k in data["keywords"][:10]]
            if "response_tone" in data:
                try:
                    result["response_tone"] = ResponseTone(data["response_tone"])
                except ValueError:
                    pass
            if "responsibility" in data:
                try:
                    result["responsibility"] = Responsibility(data["responsibility"])
                except ValueError:
                    pass
            if "urgency" in data and data["urgency"] in ("low", "medium", "high"):
                result["urgency"] = Urgency(data["urgency"])
            if "requires_response" in data:
                result["requires_response"] = bool(data["requires_response"])

            return result
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise LLMParseError(f"Failed to parse tagger response: {e}. Raw: {raw[:500]}") from e
