import pickle
import json
from typing import Tuple

from river.compose import Pipeline as Model
from src.paths import get_path_to_model_artifact

def push_model_to_registry(
    model: Model,
    name: str,
    metadata: dict,    
) -> None:
    """
    Pushes the trained model to the model registry.
    In this case, we will save the model to a file.
    In a real-world scenario, you would push the model to a model registry,
    like CometML.

    Args:
        model (Model): Trained model.
        name (str): Name of the model.
        metadata (dict): Metadata of the model.

    Returns:
        None
    """
    # save the model artifact to a pickle file
    model_file = str(get_path_to_model_artifact(f'{name}.pkl'))
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)

    # save the model metadata to json file
    model_data_file = str(get_path_to_model_artifact(f'{name}_data.json'))
    with open(model_data_file, 'w') as f:
        json.dump(metadata, f)

def load_model_from_registry(name: str) -> Tuple[Model, dict]:
    """
    Loads a model from the model registry.

    Args:
        name (str): Name of the model.

    Returns:
        Tuple[Model, dict]: Model and metadata.
    """
    model_file = str(get_path_to_model_artifact(f'{name}.pkl'))
    with open(model_file, 'rb') as f:
        model = pickle.load(f)
    
    model_data_file = str(get_path_to_model_artifact(f'{name}_data.json'))
    with open(model_data_file, 'r') as f:
        metadata = json.load(f)

    return model, metadata