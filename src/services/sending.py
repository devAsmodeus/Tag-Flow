import logging

from src.domain.entities import SendLogEntry
from src.domain.enums import Marketplace, SendStatus
from src.domain.interfaces import IResponseRepository, ISender, ISendLogRepository

logger = logging.getLogger(__name__)


class SendingService:
    def __init__(
        self,
        senders: dict[Marketplace, ISender],
        response_repo: IResponseRepository,
        send_log_repo: ISendLogRepository,
        max_retries: int = 3,
    ) -> None:
        self._senders = senders
        self._response_repo = response_repo
        self._send_log_repo = send_log_repo
        self._max_retries = max_retries

    def send_pending(self) -> int:
        sent_count = 0

        unsent = self._response_repo.get_unsent()
        for response, item in unsent:
            entry = SendLogEntry(
                response_id=response.id,
                marketplace=item.marketplace,
                external_id=item.external_id,
            )
            self._send_log_repo.insert(entry)

            success = self._try_send(item.marketplace, item.external_id, response.response_text)
            if success:
                self._send_log_repo.update_status(entry.id, SendStatus.SENT)
                sent_count += 1
            else:
                self._send_log_repo.update_status(
                    entry.id, SendStatus.FAILED, "Send attempt failed"
                )

        failed = self._send_log_repo.get_failed_for_retry(self._max_retries)
        for entry in failed:
            success = self._try_send(entry.marketplace, entry.external_id, None)
            if success:
                self._send_log_repo.update_status(entry.id, SendStatus.SENT)
                sent_count += 1
            else:
                self._send_log_repo.update_status(
                    entry.id, SendStatus.FAILED, "Retry failed"
                )

        logger.info("Sending complete: %d sent", sent_count)
        return sent_count

    def _try_send(self, marketplace: Marketplace, external_id: str, text: str | None) -> bool:
        sender = self._senders.get(marketplace)
        if not sender:
            logger.error("No sender configured for marketplace: %s", marketplace)
            return False
        if text is None:
            logger.warning("No response text available for retry of %s", external_id)
            return False
        try:
            return sender.send_response(external_id, text)
        except Exception as e:
            logger.error(
                "Send failed for %s/%s: %s",
                marketplace.value, external_id, e, exc_info=True,
            )
            return False
