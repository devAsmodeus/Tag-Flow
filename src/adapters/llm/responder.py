import logging

from src.adapters.llm.client import OllamaClient
from src.domain.entities import Item, Tag
from src.domain.interfaces import IResponder

logger = logging.getLogger(__name__)

RESPONSE_PROMPT = """Ты — представитель магазина на маркетплейсе. Напиши ответ на {item_type} покупателя.

Правила:
- Будь вежливым и профессиональным
- Обращайся на "Вы"
- Если отзыв негативный — извинись и предложи решение (обратиться в поддержку)
- Если отзыв положительный — поблагодари
- Если это вопрос — дай полезный ответ
- Ответ должен быть 2-4 предложения, не больше
- Не используй шаблонные фразы типа "Спасибо за обратную связь" в начале каждого ответа
- Будь конкретным, ссылайся на то, что написал покупатель

Тональность отзыва: {sentiment}
Тема: {topic}
Срочность: {urgency}
Оценка: {rating}

Текст покупателя:
{text}

Напиши ТОЛЬКО текст ответа, без кавычек и пояснений:"""


class OllamaResponder(IResponder):
    def __init__(self, client: OllamaClient, model: str) -> None:
        self._client = client
        self._model = model

    def generate(self, item: Item, tag: Tag) -> str:
        prompt = RESPONSE_PROMPT.format(
            item_type="отзыв" if item.item_type.value == "review" else "вопрос",
            sentiment=tag.sentiment.value if tag.sentiment else "нейтральный",
            topic=tag.topic or "общее",
            urgency=tag.urgency.value,
            rating=item.rating if item.rating else "нет оценки",
            text=item.text[:2000],
        )

        response_text = self._client.generate(self._model, prompt, timeout=180.0)
        return self._clean_response(response_text)

    @staticmethod
    def _clean_response(text: str) -> str:
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1]
        return text.strip()
