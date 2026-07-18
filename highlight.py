"""Generate highlight.css by merging two pygments themes into light-dark() colors.

Typography (bold/italic) comes from the light theme so only colour changes
between schemes. Usage:

    make highlight
"""

from pygments.styles import get_style_by_name
from pygments.token import STANDARD_TYPES

LIGHT = get_style_by_name("lovelace")
DARK = get_style_by_name("github-dark")


def colour(style, token) -> str:
    """The hex colour a style gives a token, or currentColor if it gives none"""
    value = style.style_for_token(token)["color"]
    return f"#{value}" if value else "currentColor"


print("/* lovelace (light) + github-dark (dark), see highlight.py */")
for token, name in STANDARD_TYPES.items():
    # "w" is whitespace, colouring it achieves nothing
    if not name or name in ("hll", "lineno", "w"):
        continue
    light, dark = colour(LIGHT, token), colour(DARK, token)
    if light == dark == "currentColor":
        continue
    rules = [f"color: light-dark({light}, {dark})"]
    if LIGHT.style_for_token(token)["bold"]:
        rules.append("font-weight: bold")
    if LIGHT.style_for_token(token)["italic"]:
        rules.append("font-style: italic")
    print(f".highlight .{name} {{ {'; '.join(rules)} }}")
