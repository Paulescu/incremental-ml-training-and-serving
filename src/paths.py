from pathlib import Path

def get_path_to_data_file(file_name: str) -> Path:
    """
    Returns the path to the data file with the given name.

    Args:
        file_name (str): Name of the data file.

    Returns:
        Path: Path to the data file.
    """
    path_to_this_file = Path(__file__)
    parent_directory = path_to_this_file.parent.parent
    path_to_data = parent_directory / 'data' / file_name
    return path_to_data

def get_path_to_model_artifact(file_name: str) -> Path:
    """
    Returns the path to the model artifact file with the given name.

    Args:
        file_name (str): Name of the model artifact file.

    Returns:
        Path
    """
    path_to_this_file = Path(__file__)
    parent_directory = path_to_this_file.parent.parent
    path_to_model_artifact = parent_directory / 'models' / file_name
    return path_to_model_artifact