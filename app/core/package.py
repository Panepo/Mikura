from datetime import datetime


def package_universal_cap(project_name: str, token: str) -> dict:
    """
    Packages the universal cap for the given project name and token.

    Args:
        project_name (str): The name of the project to package.
        token (str): The authentication token for Shigure.

    Returns:
        dict: A dictionary containing the path to the packaged file and the IDs used for packaging.
    """
    # Implementation of packaging logic goes here
    # For example, you might call an external script or perform some operations
    # to create the package and gather the necessary IDs.

    # Placeholder for actual implementation
    current_date = datetime.now().strftime("%Y%m%d")
    packaged_file_path = f"./data/{project_name}_{current_date}.zip"
    ids_used_for_packaging = ["id1", "id2", "id3"]  # Example IDs

    return {
        "packaged_file_path": packaged_file_path,
        "ids_used_for_packaging": ids_used_for_packaging
    }
