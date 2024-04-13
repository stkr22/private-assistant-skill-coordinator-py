import logging
import os
import pathlib
import sys
from typing import Annotated

import typer

from private_assistant_skill_coordinator import coordinator

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

app = typer.Typer()


@app.command()
def start_skill_coordinator(config_path: Annotated[pathlib.Path, typer.Argument()]):
    coordinator_obj = coordinator.Coordinator(config_path=config_path)
    coordinator_obj.run()


if __name__ == "__main__":
    start_skill_coordinator(config_path=pathlib.Path("./local_config.yaml"))
