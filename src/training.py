from pathlib import Path
import json
from datetime import datetime, timezone

from quixstreams import Application
from loguru import logger
import pandas as pd
from river import compose, linear_model, preprocessing

from src.date_utils import ms2utcstr
from src.paths import get_path_to_data_file, get_path_to_model_artifact
from src.model_registry import push_model_to_registry


def train_model_on_historical_data(path_to_historical_data: Path) -> compose.Pipeline:
    """
    Trains an initial model on the historical data and pushes it to the artifact store.

    Args:
        path_to_historical_data (Path): Path to the historical data file.

    Returns:
        compose.Pipeline: A trained model.
    """
    logger.info('Training an initial model using historical data...')

    # define the model, which is a liner model on top of the scaled features
    model = compose.Pipeline(
        preprocessing.StandardScaler(),
        linear_model.LinearRegression()
    )

    # train the model in batches
    for x in pd.read_csv(path_to_historical_data, chunksize=1024):
        
        # keep only numerical features
        x = x.select_dtypes(include=['number'])

        # drop the target variable
        y = x.pop('target_price_change_5_minutes')

        # train the model on the current batch
        model.learn_many(x, y)

    logger.info('Finished training initial model on historical data')

    # get last row from x dataframe and transform it to a dictionary
    last_timestamp = x.iloc[-1].to_dict()['timestamp']
    # transform last_timestam in milliseconds to a datetime string in UTC
    last_timestamp = ms2utcstr(last_timestamp)

    # get current UTC time as a string
    push_model_to_registry(
        model,
        name='model',
        metadata={
            'description': 'Initial model trained on historical data',
            'timestamp': last_timestamp,
        }
    )
    logger.info('Model saved to the artifact store')

    return model

def train_model_incrementally_on_live_data(
    model: compose.Pipeline,
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_consumer_group: str
) -> None:
    """"""
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
        auto_offset_reset='earliest',
    )
    topic = app.topic(name=kafka_input_topic, value_serializer='json')

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
            
            # let's use the message data to update the model
            data = json.loads(msg.value().decode('utf-8'))

            # keep only keys in data dictionary where value is numeric
            x = {k: v for k, v in data.items() if isinstance(v, (int, float))}
            
            # drop the target variable
            y = x.pop('target_price_change_5_minutes')

            # train the model on the current batch
            model.learn_one(x, y)
            logger.info('Model updated with new data')
            
            model_timestamp = ms2utcstr(data['timestamp']) 
            
            push_model_to_registry(
                model,
                name='model',
                metadata={
                    'description': 'Model trained incrementally on live data',
                    'timestamp': model_timestamp,
                }
            )
            logger.info('Model saved to the artifact store')
            
            # breakpoint()
            consumer.store_offsets(message=msg)

def train(
    path_to_historical_data: Path,
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_consumer_group: str,
) -> None:
    """
    Trains an ML model using the data from the given path.

    Args:
        path_to_historical_data (str): Path to the data file with historical data, used to train the initial model.
        kafka_broker_address (str): Address of the Kafka broker.
        kafka_input_topic (str): Name of the Kafka topic to read the input data from.
        kafka_consumer_group (str): Name of the Kafka consumer group.

    Returns:
        None
    """
    model = train_model_on_historical_data(path_to_historical_data)

    logger.info('Start incremental training of the model using live data...')
    train_model_incrementally_on_live_data(
        model=model,
        kafka_broker_address=kafka_broker_address,
        kafka_input_topic=kafka_input_topic,
        kafka_consumer_group=kafka_consumer_group,
    )

if __name__ == '__main__':

    train(
        path_to_historical_data=get_path_to_data_file('historical.csv'),
        kafka_broker_address='localhost:19092',
        kafka_input_topic='features_with_target',
        kafka_consumer_group='training_consumer_group',
    )