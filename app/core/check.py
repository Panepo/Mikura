
def check_ids(project_name: str, ids: list) -> bool:
    """
    Check if the provided IDs are valid for packaging.

    Args:
        project_name (str): The name of the project.
        ids (list): A list of string IDs to be checked.

    Returns:
        bool: True if the IDs are valid for packaging, False otherwise.
    """
    # Implement your validation logic here
    if not project_name:
        return False

    if not ids:
        return False

    new_ids = fetch_data(project_name)

    # Sort and join the lists into strings
    ids_str = "".join(sorted(ids))
    new_ids_str = "".join(sorted(new_ids))

    # Compare the two strings
    return ids_str == new_ids_str

def fetch_data(project_name: str) -> list:
    """
    Fetch the necessary data for packaging based on the project name.

    Args:
        project_name (str): The name of the project.

    Returns:
        list: A list of ids which belong to the necessary data for packaging.
    """
    # Implement your data fetching logic here
    data = ["example_data1", "example_data2"]
    return data
