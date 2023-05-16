import os
from types import SimpleNamespace

TEAM = "wandbot"
PROJECT = "wandbbot"
JOB_TYPE = "production"

ARTIFACT_ENTITY = os.getenv("WANDB_ENTITY", TEAM)

default_config = SimpleNamespace(
    faiss_artifact=f"{ARTIFACT_ENTITY}/wandb_docs_bot_dev/faiss_store:latest",
    hyde_prompt_artifact=f"{ARTIFACT_ENTITY}/wandb_docs_bot_dev/hyde_prompt:latest",
    chat_prompt_artifact=f"{ARTIFACT_ENTITY}/wandb_docs_bot_dev/system_prompt:latest",
    model_name="gpt-4",
)
