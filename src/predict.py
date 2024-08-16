from typing import Optional
import json

from quixstreams import Application
from loguru import logger

from src.model_registry import load_model_from_registry

def run(
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_consumer_group: str,
    refresh_model: Optional[bool] = False,
) -> None:
    """
    Runs the prediction application as a streaming service

    Args:
        kafka_broker_address (str): Address of the Kafka broker.
        kafka_input_topic (str): Name of the input topic.   
        kafka_consumer_group (str): Name of the Kafka consumer

    Returns:
        None
    """
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group
    )
    topic = app.topic(name=kafka_input_topic, value_serializer='json')

    # load the model from the artifact store
    model, model_data = load_model_from_registry(name='model')
    logger.info('Using model', model_data)
    
    # breakpoint()

    with app.get_consumer() as consumer:
        consumer.subscribe(topics=[topic.name])

        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                # We have a message but it is an error.
                # We just log the error and continue
                logger.error('Kafka error:', msg.error())
                continue
                   
            # let's use the message data to make a prediction
            data = json.loads(msg.value().decode('utf-8'))

            # keep only keys in data dictionary where value is numeric
            x = {k: v for k, v in data.items() if isinstance(v, (int, float))}

            # make a prediction
            y_pred = model.predict_one(x)
            logger.info(f'Prediction: {y_pred}')

            consumer.store_offsets(message=msg)

            # refresh the model
            if refresh_model:
                try:
                    model, model_data = load_model_from_registry(name='model')
                    logger.info(f'Using model trained up to {model_data["timestamp"]}')
                except Exception as e:
                    # logger.error(f'Error refreshing the model: {e}')
                    continue

if __name__ == '__main__':

    run(
        kafka_broker_address='localhost:19092',
        kafka_input_topic='features',
        kafka_consumer_group='prediction_consumer_group',
        refresh_model=True,
    )