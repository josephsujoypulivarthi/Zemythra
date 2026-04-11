import json
import threading
import urllib.parse
from functools import lru_cache
from typing import Optional, List, Dict, Generator
import ollama


OLLAMA_MODEL = "gemma3:4b"
KEEP_ALIVE = "2h"


SYSTEM_PROMPT = (
    "You are a helpful health AI assistant. "
    "Give a cautious, non-diagnostic response in plain language. "
    "Do not claim certainty. "
    "Mention urgent warning signs when relevant. "
    "Keep the answer brief, clear, and structured."
)


DEFAULT_OPTIONS = {
    "temperature": 0.2,
    "num_predict": 160,
    "num_ctx": 2048,
}


_lock = threading.Lock()
_warmed = False




def warmup_model() -> None:
    global _warmed
    if _warmed:
        return
    with _lock:
        if _warmed:
            return
        try:
            ollama.generate(
                model=OLLAMA_MODEL,
                prompt="hi",
                keep_alive=KEEP_ALIVE,
                options={"temperature": 0, "num_predict": 8, "num_ctx": 512},
            )
            _warmed = True
            print(f"{OLLAMA_MODEL} warmed successfully")
        except Exception as e:
            print(f"Warmup failed: {e}")




def _trim_text(text: str, max_chars: int = 1200) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."




def build_prompt(
    user_prompt: str,
    has_image: bool,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    parts = [SYSTEM_PROMPT]


    if has_image:
        parts.append("The user uploaded an image. Use the image with the question.")


    if chat_history:
        recent = chat_history[-3:]
        history_lines = []
        for item in recent:
            role = item.get("role", "user")
            content = _trim_text(item.get("content", ""), 300)
            history_lines.append(f"{role.title()}: {content}")
        if history_lines:
            parts.append("Recent conversation:\n" + "\n".join(history_lines))


    parts.append(f"User question: {_trim_text(user_prompt, 700)}")
    parts.append("Answer in 5 short bullet points max when possible.")


    return "\n\n".join(parts)




def _generate(
    prompt: str,
    image_bytes: Optional[bytes] = None,
    stream: bool = False,
    num_predict: int = 160,
    model: str = OLLAMA_MODEL,
):
    options = {**DEFAULT_OPTIONS, "num_predict": num_predict}


    if image_bytes:
        return ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_bytes],
                }
            ],
            keep_alive=KEEP_ALIVE,
            stream=stream,
            options=options,
        )


    return ollama.generate(
        model=model,
        prompt=prompt,
        keep_alive=KEEP_ALIVE,
        stream=stream,
        options=options,
    )




def call_ollama(
    prompt: str,
    image_bytes: Optional[bytes] = None,
    max_tokens: int = 160,
    model: str = OLLAMA_MODEL,
) -> str:
    response = _generate(
        prompt=prompt,
        image_bytes=image_bytes,
        stream=False,
        num_predict=max_tokens,
        model=model,
    )
    if image_bytes:
        return response["message"]["content"].strip()
    return response["response"].strip()




def call_ollama_stream(
    prompt: str,
    image_bytes: Optional[bytes] = None,
    max_tokens: int = 160,
    model: str = OLLAMA_MODEL,
) -> Generator[str, None, None]:
    response = _generate(
        prompt=prompt,
        image_bytes=image_bytes,
        stream=True,
        num_predict=max_tokens,
        model=model,
    )
    for chunk in response:
        if image_bytes:
            content = chunk.get("message", {}).get("content", "")
        else:
            content = chunk.get("response", "")
        if content:
            yield content




@lru_cache(maxsize=256)
def _cached_search_url(query: str, suffix: str) -> str:
    q = urllib.parse.quote_plus(f"{query} {suffix}".strip())
    return f"https://www.youtube.com/results?search_query={q}"




def generate_video_suggestions(query: str):
    q = _trim_text(query, 120)
    return [
        {"title": f"{q} explained", "url": _cached_search_url(q, "explained")},
        {"title": f"{q} symptoms", "url": _cached_search_url(q, "symptoms")},
        {"title": f"{q} when to see a doctor", "url": _cached_search_url(q, "when to see a doctor")},
    ]




def next_question_suggestions(query: str):
    q = query.lower()
    if "fever" in q:
        return ["How high is the fever?", "When should fever become urgent?", "What home care may help?"]
    if "cough" in q:
        return ["How long has the cough lasted?", "Are there breathing warning signs?", "What could make it worse?"]
    if "chest pain" in q:
        return ["When is chest pain an emergency?", "What symptoms need urgent care?", "Could this be non-cardiac pain?"]
    return [
        "What symptoms should I watch next?",
        "When should I seek medical help?",
        "What home care steps may help?",
    ]




if __name__ == "__main__":
    warmup_model()
    prompt = build_prompt(user_prompt="I have cough and mild fever for 2 days", has_image=False)
    answer = call_ollama(prompt, max_tokens=140)
    print(answer)
    print("\nStreaming:\n")
    for token in call_ollama_stream(prompt, max_tokens=140):
        print(token, end="", flush=True)
