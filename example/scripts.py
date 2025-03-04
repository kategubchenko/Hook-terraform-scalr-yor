# import requests
# import click
# import json
# import sys


# @click.group()
# def cli():
#     """
#     Scripts helper.
#     """


# @cli.command()
# @click.option(
#     "-h",
#     "--hostname",
#     type=str,
#     multiple=False,
#     help="Scalr hostname",
# )
# @click.option(
#     "-t",
#     "--token",
#     type=str,
#     multiple=False,
#     help="Scalr hostname",
# )
# @click.option(
#     "-r",
#     "--run_id",
#     type=str,
#     multiple=False,
#     help="Run identifier",
# )
# @click.option(
#     "-d",
#     "--delimiter",
#     type=str,
#     multiple=False,
#     help="Run identifier",
# )
# def get_tags(hostname: str, token: str, run_id: str, delimiter: str):
#     def _fetch(route):
#         response = requests.get(
#             f"https://{hostname}/api/iacp/v3/{route}",
#             headers={"Authorization": f"Bearer {token}", "Prefer": "profile=preview"}
#         )
#         document = response.json()
#         if response.status_code != 200:
#             raise Exception(json.dumps(document, indent=2))
#         return document

#     run = _fetch(f"runs/{run_id}?include=workspace,vcs-revision")

#     run_attributes = run["data"]["attributes"]
#     tags = {"run_id": run_id, "source": run_attributes["source"], "created-at": run_attributes["created-at"]}

#     for val in run["included"]:
#         attributes = val["attributes"]
#         if val["type"] == "workspaces":
#             tags.update({
#                 "workspace_id": val["id"],
#                 "workspace_name": attributes["name"],
#                 "environment_id": val["relationships"]["environment"]["data"]["id"],
#             })
#             tag_ids = []
#             for tag in val["relationships"].get("tags", {"data": []})["data"]:
#                 tag_ids.append(tag["id"])
#             workspace_tags = _fetch(f"tags?filter[tag]=in:{','.join(tag_ids)}")
#             for ws_tag in workspace_tags["data"]:
#                 name: str = ws_tag["attributes"]["name"]
#                 chunks = name.split(delimiter)
#                 tags.update({chunks[0]: chunks[1]})
#         elif val["type"] == "vcs-revisions":
#             tags.update(val["attributes"])
#         elif val["type"] == "tags":
#             tags.update({})

#     print(json.dumps(tags))
#     sys.exit(0)


# if __name__ == "__main__":
#     try:
#         cli()
#     except Exception as err:
#         print(str(err))
#         sys.exit(1)


#!/usr/bin/env python3
"""
Scripts helper for Scalr integration with Yor tagging tool.
Retrieves and processes tags from Scalr API.
"""

import json
import sys
from typing import Dict, Any, Optional, List

import click
import requests


@click.group()
def cli() -> None:
    """
    Scripts helper for Scalr API integration.
    """


@cli.command()
@click.option(
    "-h",
    "--hostname",
    type=str,
    required=True,
    help="Scalr hostname",
)
@click.option(
    "-t",
    "--token",
    type=str,
    required=True,
    help="Scalr API token",
)
@click.option(
    "-r",
    "--run_id",
    type=str,
    required=True,
    help="Run identifier",
)
@click.option(
    "-d",
    "--delimiter",
    type=str,
    required=False,
    default=":",
    help="Tag name delimiter character (default: ':')",
)
def get_tags(hostname: str, token: str, run_id: str, delimiter: str) -> None:
    """
    Retrieve and process tags from Scalr API.

    Args:
        hostname: Scalr hostname
        token: Scalr API token
        run_id: Run identifier
        delimiter: Character used to split tag names
    """
    try:
        tags = collect_tags(hostname, token, run_id, delimiter)
        print(json.dumps(tags))
        sys.exit(0)
    except Exception as err:
        print(str(err), file=sys.stderr)
        sys.exit(1)


def collect_tags(hostname: str, token: str, run_id: str, delimiter: str) -> Dict[str, Any]:
    """
    Collect tags and metadata from Scalr API.

    Args:
        hostname: Scalr hostname
        token: Scalr API token
        run_id: Run identifier
        delimiter: Character used to split tag names

    Returns:
        Dictionary with collected tags and metadata

    Raises:
        Exception: If API request fails
    """
    run = _fetch_api_data(hostname, token, f"runs/{run_id}?include=workspace,vcs-revision")

    # Захист від None-значень у відповіді API
    if not run or "data" not in run or run["data"] is None:
        return {"run_id": run_id, "error": "No valid data received from API"}

    run_data = run["data"]
    run_attributes = run_data.get("attributes", {})

    tags = {
        "run_id": run_id,
        "source": run_attributes.get("source", "unknown"),
        "created-at": run_attributes.get("created-at", "unknown")
    }

    included = run.get("included", [])
    if included and isinstance(included, list):
        for val in included:
            if not val or not isinstance(val, dict):
                continue

            val_type = val.get("type")
            attributes = val.get("attributes", {})

            if val_type == "workspaces":
                workspace_tags = _process_workspace_data(val, attributes, hostname, token, delimiter)
                tags.update(workspace_tags or {})
            elif val_type == "vcs-revisions" and attributes:
                tags.update(attributes)

    return tags


def _process_workspace_data(
        workspace_data: Optional[Dict[str, Any]],
        attributes: Dict[str, Any],
        hostname: str,
        token: str,
        delimiter: str
) -> Dict[str, Any]:
    """
    Process workspace data and retrieve associated tags.

    Args:
        workspace_data: Workspace data from API
        attributes: Workspace attributes
        hostname: Scalr hostname
        token: Scalr API token
        delimiter: Character used to split tag names

    Returns:
        Dictionary with workspace tags and metadata
    """
    if not workspace_data or not isinstance(workspace_data, dict):
        return {}

    workspace_id = workspace_data.get("id", "unknown")
    workspace_tags = {
        "workspace_id": workspace_id,
        "workspace_name": attributes.get("name", "unknown"),
    }

    relationships = workspace_data.get("relationships", {})
    if relationships and isinstance(relationships, dict):
        environment = relationships.get("environment", {})
        if environment and isinstance(environment, dict):
            env_data = environment.get("data", {})
            if env_data and isinstance(env_data, dict):
                workspace_tags["environment_id"] = env_data.get("id", "unknown")

    tag_ids = _extract_tag_ids(relationships)

    if tag_ids:
        try:
            ws_tags_data = _fetch_api_data(
                hostname, token, f"tags?filter[tag]=in:{','.join(tag_ids)}"
            )

            if ws_tags_data and "data" in ws_tags_data:
                tags_data = ws_tags_data["data"]
                if tags_data and isinstance(tags_data, list):
                    for ws_tag in tags_data:
                        if not ws_tag or not isinstance(ws_tag, dict):
                            continue

                        attributes = ws_tag.get("attributes", {})
                        if not attributes:
                            continue

                        name = attributes.get("name")
                        if name and isinstance(name, str) and delimiter in name:
                            try:
                                key, value = name.split(delimiter, 1)
                                workspace_tags[key] = value
                            except ValueError:
                                continue
        except Exception as e:
            workspace_tags["tags_error"] = str(e)

    return workspace_tags


def _extract_tag_ids(relationships: Optional[Dict[str, Any]]) -> List[str]:
    """

    Args:
        relationships: Словник з відносинами об'єкта

    Returns:
        List of tag IDs
    """
    tag_ids = []

    if not relationships or not isinstance(relationships, dict):
        return tag_ids

    tags_rel = relationships.get("tags")
    if not tags_rel or not isinstance(tags_rel, dict):
        return tag_ids

    data = tags_rel.get("data")
    if not data or not isinstance(data, list):
        return tag_ids

    for tag in data:
        if tag and isinstance(tag, dict) and "id" in tag:
            tag_ids.append(tag["id"])

    return tag_ids


def _fetch_api_data(hostname: str, token: str, route: str) -> Dict[str, Any]:
    """
    Fetch data from Scalr API.

    Args:
        hostname: Scalr hostname
        token: Scalr API token
        route: API route to fetch

    Returns:
        API response data as dictionary

    Raises:
        Exception: If API request fails
    """
    try:
        response = requests.get(
            f"https://{hostname}/api/iacp/v3/{route}",
            headers={"Authorization": f"Bearer {token}", "Prefer": "profile=preview"},
            timeout=30
        )

        if not response.content:
            return {}

        document = response.json()
        if response.status_code != 200:
            raise Exception(json.dumps(document, indent=2))

        return document
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        return {}


if __name__ == "__main__":
    cli()
