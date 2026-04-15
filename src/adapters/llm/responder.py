import logging

from src.adapters.llm.client import OllamaClient
from src.domain.entities import Item, Tag
from src.domain.interfaces import IResponder

logger = logging.getLogger(__name__)

RESPONSE_PROMPT = """Ты — представитель магазина-продавца на маркетплейсе Wildberries. Напиши ответ на {item_type} покупателя.

ЗОНЫ ОТВЕТСТВЕННОСТИ (строго соблюдай):
- ПРОДАВЕЦ отвечает за: качество товара, комплектацию, описание, упаковку товара перед отправкой
- WILDBERRIES отвечает за: доставку, работу ПВЗ (пунктов выдачи), поведение сотрудников ПВЗ, повреждения при транспортировке
- Если проблема в зоне Wildberries (доставка, ПВЗ, повреждение при перевозке) — НЕ извиняйся за неё, НЕ бери ответственность. Вежливо объясни, что доставка и работа ПВЗ — это зона ответственности маркетплейса, и посоветуй обратиться в поддержку Wildberries.

ЗАПРЕТЫ (никогда не делай):
- НЕ обещай возврат, обмен, замену, компенсацию — ты не уполномочен принимать такие решения
- НЕ пиши "мы вернём деньги", "обеспечим замену", "возместим стоимость", "организуем доставку"
- НЕ пиши "мы проведём разбирательство" по вопросам ПВЗ/доставки
- НЕ начинай ответ с "Извините за неудобства" — это шаблонно и неестественно
- НЕ используй фразы: "Спасибо за обратную связь", "Спасибо за ваш отзыв" как первое предложение
- НЕ повторяй одинаковые конструкции в каждом ответе

ФОРМАТ ОТВЕТА:
- ВСЕГДА начинай с приветствия: "Здравствуйте!" или "Добрый день!"
- Пиши естественно, как живой человек, а не бот
- Каждый ответ должен быть уникальным — ссылайся на конкретные детали из отзыва
- 2-4 предложения (не считая инструкцию для чата и приветствие)
- Обращайся на "Вы"

ИНСТРУКЦИЯ ДЛЯ ЧАТА (добавляй при проблемах с товаром продавца):
Если покупатель жалуется на комплектацию, брак, качество товара и ответственный — продавец, в конце ответа добавь:
"Для того, чтобы написать нам в чат, зайдите в покупки в личном кабинете, выберите товар по которому хотите задать вопрос, нажмите три точки в правом верхнем углу и выберите «задать вопрос продавцу»."

Тональность: {sentiment}
Эмоция покупателя: {emotion}
Тема: {topic}
Детали: {subtopic}
Проблема с товаром: {product_issue}
Намерение покупателя: {intent}
Рекомендуемый тон ответа: {response_tone}
Ответственный за проблему: {responsibility}
Срочность: {urgency}
Оценка: {rating}

Текст покупателя:
{text}

Напиши ТОЛЬКО текст ответа, без кавычек и пояснений.

/nothink
"""


class OllamaResponder(IResponder):
    def __init__(self, client: OllamaClient, model: str) -> None:
        self._client = client
        self._model = model

    def generate(self, item: Item, tag: Tag) -> str:
        prompt = RESPONSE_PROMPT.format(
            item_type="отзыв" if item.item_type.value == "review" else "вопрос",
            sentiment=tag.sentiment.value if tag.sentiment else "нейтральный",
            emotion=tag.emotion.value if tag.emotion else "не определена",
            topic=tag.topic or "общее",
            subtopic=tag.subtopic or "не указано",
            product_issue=tag.product_issue or "нет",
            intent=tag.intent.value if tag.intent else "не определено",
            response_tone=tag.response_tone.value if tag.response_tone else "informational",
            responsibility=tag.responsibility.value if tag.responsibility else "seller",
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
