from src.adapters.collectors import OzonCollector, WildberriesCollector, YandexCollector
from src.adapters.llm import OllamaClient, OllamaResponder, OllamaTagger
from src.adapters.senders import OzonSender, WildberriesSender, YandexSender
from src.domain.enums import Marketplace
from src.infrastructure.circuit_breaker import (
    ollama_breaker,
    ozon_breaker,
    wb_breaker,
    yandex_breaker,
)
from src.infrastructure.config import Settings
from src.infrastructure.database import Database
from src.repositories import ItemRepository, ResponseRepository, SendLogRepository, TagRepository
from src.services import (
    CollectionService,
    PipelineService,
    ResponseService,
    SendingService,
    TaggingService,
)


class Container:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.db = Database(settings.database_url)

        self.item_repo = ItemRepository(self.db)
        self.tag_repo = TagRepository(self.db)
        self.response_repo = ResponseRepository(self.db)
        self.send_log_repo = SendLogRepository(self.db)

        self.ollama = OllamaClient(settings.ollama_url, breaker=ollama_breaker)
        self.tagger = OllamaTagger(self.ollama, settings.tagger_model)
        self.responder = OllamaResponder(self.ollama, settings.responder_model)

        self.collectors = [
            WildberriesCollector(
                settings.wb_token, breaker=wb_breaker, batch_size=settings.batch_size
            ),
            OzonCollector(
                settings.ozon_client_id, settings.ozon_api_key,
                breaker=ozon_breaker, batch_size=settings.batch_size,
            ),
            YandexCollector(
                settings.ym_token, settings.ym_business_id,
                breaker=yandex_breaker, batch_size=settings.batch_size,
            ),
        ]

        self.senders = {
            Marketplace.WB: WildberriesSender(settings.wb_token),
            Marketplace.OZON: OzonSender(settings.ozon_client_id, settings.ozon_api_key),
            Marketplace.YANDEX: YandexSender(settings.ym_token, settings.ym_business_id),
        }

        self.collection_service = CollectionService(self.collectors, self.item_repo)
        self.tagging_service = TaggingService(self.tagger, self.item_repo, self.tag_repo)
        self.response_service = ResponseService(
            self.responder, self.tag_repo, self.response_repo
        )
        self.sending_service = SendingService(
            self.senders, self.response_repo, self.send_log_repo, settings.max_retries
        )
        self.pipeline = PipelineService(
            self.collection_service,
            self.tagging_service,
            self.response_service,
            self.sending_service,
            self.db,
        )

    def close(self) -> None:
        self.ollama.close()
        self.db.close()
