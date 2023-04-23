import os
from functools import partial

import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from wandbot.apps.slack.config import SlackAppConfig

config = SlackAppConfig()
app = App(token=config.SLACK_APP_TOKEN)


def format_response(user: str, response):
    if response is not None:
        if config.include_sources:
            result = (
                response["answer"]
                + "\n\n**References**\n\n"
                + "- ".join(response["sources"].splitlines())
            )
        else:
            result = response["answer"]

        output = f"Hi <@{user}>:\n\n{result}"
    else:
        output = f"Hi <@{user}>:\n\n {config.ERROR_MESSAGE}"
    return output


def run_api_query(query: str, thread_id: str, event_id: str):
    try:
        query = {
            "question": query,
            "question_answer_id": event_id,
            "thread_id": thread_id,
            "application": "slack",
        }
        query_url = f"{config.WANDBOT_API_URL}/query"

        response = requests.post(query_url, json=query)
        if response.status_code == 200:
            response = response.json()
            return response
    except:
        return None


def send_api_feedback(feedback: str, thread_id: str, question_answer_id: str):
    feedback_url: config.WANDBOT_API_URL + "/feedback"
    feedback_obj = {
        "feedback": feedback,
        "question_answer_id": question_answer_id,
        "thread_id": thread_id,
    }
    response = requests.post(feedback_url, json=feedback_obj)
    if response.status_code == 200:
        return response.json()


def send_message(say, message, thread=None):
    if thread is not None:
        return say(text=message, thread_ts=thread)
    else:
        return say(text=message)


@app.event("app_mention")
def command_handler(body, say, logger):
    try:
        query = body["event"].get("text")
        user = body["event"].get("user")
        thread_id = body["event"].get("thread_ts", None) or body["event"].get(
            "ts", None
        )
        event_id = body["event"].get("event_id", None)
        say = (partial(say, token=config.SLACK_BOT_TOKEN),)
        # send out the intro message
        send_message(
            say=say,
            message=f"Hi <@{user}>:\n\n{config.INTRO_MESSAGE}",
            thread=thread_id,
        )

        # process the query through the api
        api_response = run_api_query(query, thread_id, event_id)
        response = format_response(user, api_response)

        # send the response
        send_message(say=say, message=response, thread=thread_id)

        # send the outro message
        outro_sent = send_message(
            say=say, message=config.OUTRO_MESSAGE, thread=thread_id
        )

        app.client.reactions_add(
            channel=body["event"]["channel"],
            timestamp=outro_sent["ts"],
            name="thumbsup",
            token=config.SLACK_BOT_TOKEN,
        )
        app.client.reactions_add(
            channel=body["event"]["channel"],
            timestamp=outro_sent["ts"],
            name="thumbsdown",
            token=config.SLACK_BOT_TOKEN,
        )
    except Exception as e:
        logger.error(f"Error posting message: {e}")


@app.event("reaction_added")
def handle_reaction_added(event, say):
    channel_id = event["item"]["channel"]
    message_ts = event["item"]["ts"]
    result = app.client.conversations_history(
        channel=channel_id,
        latest=message_ts,
        limit=1,
        inclusive=True,
        token=config.SLACK_BOT_TOKEN,
    )

    # TODO: Add feedback handling

    # if result["ok"] and len(result["messages"]) > 0:
    #     # TODO: More robust way to handle feedback. This will base it on the first message in the thread
    #     # BUG: Message also returns the user info so stripping that before update
    #     query = result["messages"][0]["text"]
    #     if query is not None and isinstance(query, str):
    #         query = remove_angle_brackets_and_whitespace(query)
    #     user = event["user"]
    #     feedback = None
    #     print(str(event["reaction"]))
    #     if "+1" in str(event["reaction"]):
    #         feedback = "positive"
    #     if "-1" in str(event["reaction"]):
    #         feedback = "negative"
    #     if feedback:
    #         print("added feedback")
    #         slack_adapter.update_feedback_in_db(user, query, feedback)
    #     else:
    #         print(f"Unhandled reaction: {event['reaction']} in channel {channel_id}")
    # else:
    #     print(
    #         f"Unable to retrieve message for reaction {event['reaction']} in channel {channel_id}"
    #     )


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()