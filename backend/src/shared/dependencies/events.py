from typing import Annotated

from fastapi import Depends

from src.core.broker import rabbit_broker
from src.event_config import EVENT_TOPIC_MAP
from src.shared.domain.events import EventPublisher
from src.shared.infra.events import FastStreamEventPublisher


def get_event_publisher() -> FastStreamEventPublisher:
    return FastStreamEventPublisher(rabbit_broker, event_topic_map=EVENT_TOPIC_MAP)


EventPublisherDep = Annotated[EventPublisher, Depends(get_event_publisher)]
