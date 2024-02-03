import openai

from src.config import OPENAI_EXPANDER_MODEL, OPENAI_SYSTEM_EXPANDER_PROMPT


def expand_musical_description(input_text: str, max_tokens: int = 500):
    if not input_text:
        return None
    return (chunk.choices[0].delta.content or "" for chunk in openai.chat.completions.create(
        model=OPENAI_EXPANDER_MODEL,
        messages=[
            {
                "role": "system",
                "content": OPENAI_SYSTEM_EXPANDER_PROMPT
            },
            {
                "role": "user",
                "content": input_text
            }
        ],
        max_tokens=max_tokens,
        n=1,
        temperature=0.9,
        stream=True,
        timeout=60 * 1000
    ) if chunk.choices[0].delta is not None)
