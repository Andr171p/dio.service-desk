from faststream.rabbit import RabbitBroker
from faststream.rabbit.fastapi import RabbitRouter

from .settings import settings

rabbit_router = RabbitRouter(settings.rabbit.url, virtualhost=settings.rabbit.virtualhost)


def get_rabbit_broker() -> RabbitBroker:
    return rabbit_router.broker


rabbit_broker = get_rabbit_broker()
