import openai

from src.config import OPENAI_EXPANDER_MODEL, OPENAI_SYSTEM_EXPANDER_PROMPT


def expand_text(input_text):
    return openai.chat.completions.create(
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
        max_tokens=int(len(input_text) * 2),
        n=1,
        stream=True
    )
