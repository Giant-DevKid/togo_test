import json
import os

from groq import Groq


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_ai(
    system_prompt,
    message,
    temperature=0.1
):

    response = (
        client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        )
    )

    return (
        response
        .choices[0]
        .message
        .content
    )


def ask_ai_json(
    system_prompt,
    message
):

    try:

        return json.loads(
            ask_ai(
                system_prompt,
                message
            )
        )

    except Exception:

        return {}