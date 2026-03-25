from unittest.mock import MagicMock

import pytest

from src.adapters.llm.tagger import OllamaTagger
from src.domain.entities import Item
from src.domain.enums import ItemType, Marketplace, Sentiment, Urgency
from src.domain.exceptions import LLMParseError


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def tagger(mock_client):
    return OllamaTagger(mock_client, "qwen3:8b")


@pytest.fixture
def sample_item():
    return Item(
        id=1,
        marketplace=Marketplace.WB,
        item_type=ItemType.REVIEW,
        external_id="123",
        text="Отличный товар, очень доволен покупкой!",
        rating=5,
    )


def test_tag_positive_review(tagger, mock_client, sample_item):
    mock_client.generate.return_value = '{"sentiment": "positive", "topic": "качество", "urgency": "low", "requires_response": true}'

    tag = tagger.tag(sample_item)

    assert tag.sentiment == Sentiment.POSITIVE
    assert tag.topic == "качество"
    assert tag.urgency == Urgency.LOW
    assert tag.requires_response is True
    assert tag.model_name == "qwen3:8b"


def test_tag_negative_review(tagger, mock_client, sample_item):
    sample_item.rating = 1
    mock_client.generate.return_value = '{"sentiment": "negative", "topic": "брак", "urgency": "high", "requires_response": true}'

    tag = tagger.tag(sample_item)

    assert tag.sentiment == Sentiment.NEGATIVE
    assert tag.urgency == Urgency.HIGH


def test_tag_with_extra_text_around_json(tagger, mock_client, sample_item):
    mock_client.generate.return_value = 'Here is the result:\n{"sentiment": "neutral", "topic": "доставка", "urgency": "medium", "requires_response": false}\nDone!'

    tag = tagger.tag(sample_item)

    assert tag.sentiment == Sentiment.NEUTRAL
    assert tag.topic == "доставка"
    assert tag.requires_response is False


def test_tag_invalid_json_raises(tagger, mock_client, sample_item):
    mock_client.generate.return_value = "not a json at all"

    with pytest.raises(LLMParseError):
        tagger.tag(sample_item)


def test_tag_question(tagger, mock_client):
    item = Item(
        id=2,
        marketplace=Marketplace.OZON,
        item_type=ItemType.QUESTION,
        external_id="456",
        text="Подскажите, есть ли размер XL?",
    )
    mock_client.generate.return_value = '{"sentiment": "neutral", "topic": "размер", "urgency": "medium", "requires_response": true}'

    tag = tagger.tag(item)

    assert tag.requires_response is True
    assert tag.item_id == 2
