from faststream import FastStream
from app.messaging.broker import broker
import app.workers.consumers.payment

app = FastStream(broker)
