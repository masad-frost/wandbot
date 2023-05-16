from types import SimpleNamespace

TEAM = "wandbot"
PROJECT = "wandbbot"
JOB_TYPE = "production"

default_config = SimpleNamespace(
    faiss_artifact="jeffr/wandb_docs_bot_dev/faiss_store:latest",
    hyde_prompt_artifact="jeffr/wandb_docs_bot_dev/hyde_prompt:latest",
    chat_prompt_artifact="jeffr/wandb_docs_bot_dev/system_prompt:latest",
    model_name="gpt-4",
)
