import requests
import click
import json
import sys


@click.group()
def cli():
    """
    Scripts helper.
    """


@cli.command()
@click.option(
    "-h",
    "--hostname",
    type=str,
    multiple=False,
    help="Scalr hostname",
)
@click.option(
    "-t",
    "--token",
    type=str,
    multiple=False,
    help="Scalr hostname",
)
@click.option(
    "-r",
    "--run_id",
    type=str,
    multiple=False,
    help="Run identifier",
)
@click.option(
    "-d",
    "--delimiter",
    type=str,
    multiple=False,
    help="Run identifier",
)
def get_tags(hostname: str, token: str, run_id: str, delimiter: str):
    def _fetch(route):
        response = requests.get(
            f"https://{hostname}/api/iacp/v3/{route}",
            headers={"Authorization": f"Bearer {token}", "Prefer": "profile=preview"}
        )
        document = response.json()
        if response.status_code != 200:
            raise Exception(json.dumps(document, indent=2))
        return document

    run = _fetch(f"runs/{run_id}?include=workspace,vcs-revision")

    run_attributes = run["data"]["attributes"]
    tags = {"run_id": run_id, "source": run_attributes["source"], "created-at": run_attributes["created-at"]}

    for val in run["included"]:
        attributes = val["attributes"]
        if val["type"] == "workspaces":
            tags.update({
                "workspace_id": val["id"],
                "workspace_name": attributes["name"],
                "environment_id": val["relationships"]["environment"]["data"]["id"],
            })
            tag_ids = []
            for tag in val["relationships"].get("tags", {"data": []})["data"]:
                tag_ids.append(tag["id"])
            workspace_tags = _fetch(f"tags?filter[tag]=in:{','.join(tag_ids)}")
            for ws_tag in workspace_tags["data"]:
                name: str = ws_tag["attributes"]["name"]
                chunks = name.split(delimiter)
                tags.update({chunks[0]: chunks[1]})
        elif val["type"] == "vcs-revisions":
            tags.update(val["attributes"])
        elif val["type"] == "tags":
            tags.update({})

    print(json.dumps(tags))
    sys.exit(0)


if __name__ == "__main__":
    cli()