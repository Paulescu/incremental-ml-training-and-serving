from typing import Any, Optional
from time import sleep

from quixstreams import Application
from loguru import logger
import pandas as pd

class Buffer:
    """
    A buffer to store the last `max_size` elements.
    """
    def __init__(self, max_size: int):
        self._data = []
        self.max_size = max_size
    
    def append(self, data: Any):
        """
        Appends the given data to the buffer. If the buffer is full, the oldest element
        is removed.
        """
        self._data.append(data)
        if len(self._data) > self.max_size:
            self._data.pop(0)

    def get_delayed_observation(self) -> Any:
        """
        Returns the first elements of the buffer, which is the oldest observation, if
        the buffer is full. Otherwise, returns None.
        """
        if len(self._data) < self.max_size:
            return None

        return self._data[0]
    
    def __len__(self):
        return len(self._data)
    
    def __repr__(self):
        return str(self._data)


def run(
    path_to_live_data: str,
    kafka_broker_address: str,
    kafka_topic_features: str,
    kafka_topic_features_with_target: str,
    delay_target: int,
    target_name: Optional[str] = 'target_price_change_5_minutes',
) -> None:
    """
    Generates live data with features, and potentially targets too, and saves it
    to the given `kafka_topic`.

    Args:
        path_to_live_data (str): Path to the live data file.
        kafka_broker_address (str): Address of the Kafka broker.
        kafka_topic_features (str): Name of the Kafka topic to save the features.
        kafka_topic_features_with_target (str): Name of the Kafka topic to save the features with targets.
        delay_target (int): Number of observations to delay the target.
        target_name (str): Name of the target variable.

    Returns:
        None
    """
    app = Application(broker_address=kafka_broker_address)

    # topics to which the data will be sent
    # only features
    topic_features = app.topic(name=kafka_topic_features, value_serializer='json')
    # delayed features with target
    topic_features_with_target = app.topic(name=kafka_topic_features_with_target, value_serializer='json')

    # load the data as a pandas DataFrame
    data = pd.read_csv(path_to_live_data)
    features_names = [x for x in data.columns.tolist() if x != target_name]

    # transform the data to a list of dictionaries
    data = data.to_dict(orient='records')
    
    # buffer to store the last `delay_targets` rows
    buffer = Buffer(max_size=delay_target)

    with app.get_producer() as producer_of_features:
        
        with app.get_producer() as producer_of_features_with_targets:

            for d in data:
            # while True:
                
                # get the next observation
                # d = data.pop(0)

                # Push the features to the `topic_features` topic
                features = {k: v for k, v in d.items() if k in features_names}
                message = topic_features.serialize(key=None, value=features)
                producer_of_features.produce(
                    topic=topic_features.name,
                    key=message.key,
                    value=message.value
                )
                logger.info(f'Message sent to Kafka topic {topic_features.name}: {message.value}')

                # Send the features with target to the `topic_features_with_target` topic
                # add observation to the buffer
                buffer.append(d)
                # get the delayed (features, target) from the buffer
                features_with_target = buffer.get_delayed_observation()
                # if there is a delayed observation, push it to the topic
                if features_with_target is not None:
                    message = topic_features_with_target.serialize(
                        key=None, value=features_with_target)
                    producer_of_features_with_targets.produce(
                        topic=topic_features_with_target.name,
                        value=message.value,
                        key=message.key,
                    )
                    logger.info(f'Message sent to Kafka topic {topic_features.name}: {message.value}')

                # sleep for a second
                sleep(1)

if __name__ == '__main__':

    from src.paths import get_path_to_data_file
    run(
        path_to_live_data=get_path_to_data_file('live.csv'),
        kafka_broker_address='localhost:19092',
        kafka_topic_features='features',
        kafka_topic_features_with_target='features_with_target',
        delay_target=5,
    )