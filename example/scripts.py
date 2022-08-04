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
def get_tags(hostname: str, token: str, run_id: str):
    run = requests.get(
        f"https://{hostname}/api/iacp/v3/runs/{run_id}?include=workspace,vcs-revision",
        headers={"Authorization": f"Bearer {token}", "Prefer": "profile=preview"}
    ).json()

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

            if attributes["tags"]:
                tags.update(attributes["tags"])

        elif val["type"] == "vcs-revisions":
            tags.update(val["attributes"])

    print(json.dumps(tags))
    sys.exit(0)


if __name__ == "__main__":
    cli()