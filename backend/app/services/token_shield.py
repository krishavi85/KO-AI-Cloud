from app.config import settings


def compress_messages(messages):
    total = sum(len(m.content) for m in messages)
    if total <= settings.MAX_INPUT_CHARS:
        return messages, False

    system = [m for m in messages if m.role == "system"]
    non_system = [m for m in messages if m.role != "system"]
    older = non_system[:-6]
    recent = non_system[-6:]
    older_text = "\n".join([f"{m.role}: {m.content}" for m in older])[:5000]

    class Msg:
        def __init__(self, role, content):
            self.role = role
            self.content = content

    compressed = []
    compressed.extend(system)
    compressed.append(Msg("system", "Compressed older conversation memory:\n" + older_text))
    compressed.extend(recent)
    return compressed, True


def output_limit(requested):
    if requested is None:
        return settings.MAX_OUTPUT_TOKENS
    return min(requested, settings.MAX_OUTPUT_TOKENS)
