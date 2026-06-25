from faststream import FastStream

from app.infrastructure.messaging.broker import broker
import app.presentation.consumers.payment_consumer

app = FastStream(broker)
