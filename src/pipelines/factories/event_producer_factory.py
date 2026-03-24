from ..application.policies import EventProducer

from ..application.runners.events.trading212_event_producer import Trading212EventProducer

from ..infrastructure.kafka.producer_origins import Trading212AssetAPIOrigin
from ..infrastructure.kafka.producer_destination import Trading212KafkaDestination

EVENT_PRODUCER_REGISTERY = {}


def register(name: str):
    def decorator(builder):
        EVENT_PRODUCER_REGISTERY[name] = builder
        return builder

    return decorator


class EventProducerFactory:
    @staticmethod
    def get(name: str) -> EventProducer:
        return EVENT_PRODUCER_REGISTERY[name]()

    @register("trading212AssetEventProducer")
    def build_trading212_asset_event_producer() -> EventProducer:
        return Trading212EventProducer(
            origin=Trading212AssetAPIOrigin("Trading212_Asset_API"),
            destination=Trading212KafkaDestination("Kafka"),
        )
