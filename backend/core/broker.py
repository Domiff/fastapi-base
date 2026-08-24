import taskiq_fastapi
from taskiq import SmartRetryMiddleware, TaskiqEvents, TaskiqState
from taskiq_aio_pika import AioPikaBroker, Exchange, Queue

from backend.core.config import settings
from backend.core.logging import setup_logging

name = settings.app.APP_NAME

broker = AioPikaBroker(
    settings.rabbit.RABBITMQ_URL,
    qos=1,
    exchange=Exchange(name=name),
    task_queues=[Queue(name=name)],
    dead_letter_queue=Queue(name=f"{name}.dead"),
    delay_queue=Queue(name=f"{name}.delay"),
).with_middlewares(
    SmartRetryMiddleware(
        default_retry_count=settings.taskiq.TASKIQ_RETRY_COUNT,
        default_delay=settings.taskiq.TASKIQ_RETRY_DELAY,
        use_jitter=True,
        use_delay_exponent=True,
        max_delay_exponent=120,
    )
)

taskiq_fastapi.init(broker, "backend.main:app")


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    setup_logging()
