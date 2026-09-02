from app.core.fetch import fetch_ids

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

    new_ids = fetch_ids(project_name)

    # Sort and join the lists into strings
    ids_str = "".join(sorted(ids))
    new_ids_str = "".join(sorted(new_ids))

    # Compare the two strings
    return ids_str != new_ids_str
