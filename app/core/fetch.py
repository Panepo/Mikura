from fastapi import HTTPException

from app.core.config import get_settings
from app.service import shigure_client

settings = get_settings()


def _parse_version(ver):
    """Parse version string to a comparable tuple of integers, stripping trailing zeros."""
    if ver is None:
        return (0,)
    try:
        ver_str = str(ver).split('+')[0].split('-')[0]
        parts = [int(x) for x in ver_str.split('.') if x.isdigit()]
        while len(parts) > 1 and parts[-1] == 0:
            parts.pop()
        return tuple(parts) if parts else (0,)
    except Exception:
        return (0,)


async def fetch_ids(project_name: str, token: str | None = None) -> list:
    """
    Fetch the necessary data for packaging based on the project name.

    Args:
        project_name (str): The name of the project.
        token (str): The authentication token.
    Returns:
        list: A list of ids which belong to the necessary data for packaging.
    """
    if not token:
        token = settings.shigure_token

    if not token:
        raise HTTPException(status_code=500, detail="SHIGURE_TOKEN is not configured")

    # Implement your data fetching logic here
    data = ["example_data1", "example_data2"]
    return data


async def fetch_data(project_name: str, token: str | None = None) -> dict:
    """
    Fetch the necessary driver and app data for packaging based on the project name.

    Args:
        project_name (str): The name of the project.
        token (str): The authentication token.
    Returns:
        dict: A dictionary containing driver and app data records for the project.
    """
    if not token:
        token = settings.shigure_token

    if not token:
        raise HTTPException(status_code=500, detail="SHIGURE_TOKEN is not configured")

    # Fetch driver data by project
    drivers_data = await shigure_client.find_one("DRIVERPRJ", project_name, token)

    # Fetch app data by project
    apps_data = await shigure_client.find_one("APPPRJ", project_name, token)

    # Filter apps_data by categoryId, keeping only the record with the largest appver for each category
    if apps_data and isinstance(apps_data, list):
        apps_by_category = {}
        for app in apps_data:
            category_id = app.get("categoryId")
            appver = app.get("appver", "0")
            if category_id not in apps_by_category:
                apps_by_category[category_id] = app
            else:
                current_best_appver = apps_by_category[category_id].get("appver", "0")
                if _parse_version(appver) > _parse_version(current_best_appver):
                    apps_by_category[category_id] = app
        apps_data = list(apps_by_category.values())

    # Filter drivers_data by categoryId and controllerId, keeping only the record with the largest driverVer for each group
    if drivers_data and isinstance(drivers_data, list):
        drivers_by_group = {}
        for driver in drivers_data:
            category_id = driver.get("categoryId")
            controller_id = driver.get("controllerId")
            driver_ver = driver.get("driverVer", "0")
            group_key = (category_id, controller_id)
            if group_key not in drivers_by_group:
                drivers_by_group[group_key] = driver
            else:
                current_best_driver_ver = drivers_by_group[group_key].get("driverVer", "0")
                if _parse_version(driver_ver) > _parse_version(current_best_driver_ver):
                    drivers_by_group[group_key] = driver
        drivers_data = list(drivers_by_group.values())

    # Return combined data
    return {
        "drivers": drivers_data,
        "apps": apps_data,
    }
