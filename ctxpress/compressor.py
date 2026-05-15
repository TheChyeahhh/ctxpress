from __future__ import annotations

from dataclasses import dataclass

LEVELS = {
    "light":  {"target_pct": 70, "description": "Remove filler, merge redundancy. Keep almost everything meaningful."},
    "medium": {"target_pct": 40, "description": "Extract key points. Summarize verbose sections. Preserve all critical data."},
    "heavy":  {"target_pct": 15, "description": "Bullet-point extraction only. Absolute essentials. Maximum compression."},
}

# Things that must NEVER be dropped regardless of level
ALWAYS_PRESERVE = [
    "Named entities (people, companies, products, places)",
    "All numbers, dates, percentages, measurements, and dollar amounts",
    "Code blocks, commands, file paths, and URLs",
    "Decisions made and conclusions reached",
    "Action items and next steps",
    "Errors, warnings, risks, and blockers",
    "Technical specifications and requirements",
    "Direct quotes and attributed statements",
]

LEVEL_INSTRUCTIONS = {
    "light": (
        "Remove filler phrases, pleasantries, and redundant restatements. "
        "Merge sentences that repeat the same idea. "
        "Keep the original structure and flow where possible. "
        "Target: retain about 70% of the original content."
    ),
    "medium": (
        "Aggressively summarize verbose paragraphs into 1-2 sentences. "
        "Eliminate all redundancy, pleasantries, and non-essential context. "
        "Convert long explanations into tight, information-dense sentences. "
        "Use bullet points for lists of items. "
        "Target: retain about 40% of the original content."
    ),
    "heavy": (
        "Convert the entire text into a tight bullet-point list of facts and decisions. "
        "Every bullet must contain a concrete piece of information — no meta-commentary. "
        "Strip all narrative, explanation, and context that doesn't add new facts. "
        "Target: retain about 15% of the original content. This is maximum compression."
    ),
}


@dataclass
class CompressionResult:
    compressed: str
    original_chars: int
    compressed_chars: int
    ratio: float
    level: str

    @property
    def saved_pct(self) -> int:
        return round((1 - self.ratio) * 100)


def build_prompt(text: str, level: str) -> str:
    config = LEVELS.get(level, LEVELS["medium"])
    instructions = LEVEL_INSTRUCTIONS.get(level, LEVEL_INSTRUCTIONS["medium"])
    preserve_list = "\n".join(f"  • {item}" for item in ALWAYS_PRESERVE)

    return f"""You are a precision context compressor for AI systems.

Your job: compress the text below while retaining every piece of meaningful information.

Compression level: {level.upper()} (~{config["target_pct"]}% of original)
{config["description"]}

Instructions:
{instructions}

ALWAYS PRESERVE — never drop these regardless of compression level:
{preserve_list}

NEVER:
- Change facts, numbers, or named entities
- Omit decisions, action items, or risks
- Remove code, commands, or technical specs
- Add new information not in the original

Respond with ONLY the compressed text. No preamble, no explanation, no meta-commentary about what you did.

---
{text}"""


def estimate_tokens(char_count: int) -> int:
    """Rough token estimate: ~4 chars per token."""
    return max(1, char_count // 4)
