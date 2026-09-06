import re

from taxonomy import SKILL_TAXONOMY


def extract_skills(text: str) -> list[str]:
    """
    Extract normalized skills from text
    using the controlled skill taxonomy.
    """

    if not text:
        return []

    text = text.lower()

    found_skills = []

    for category, skills in SKILL_TAXONOMY.items():

        for skill, aliases in skills.items():

            for alias in aliases:

                pattern = (
                    r"(?<!\w)"
                    + re.escape(alias.lower())
                    + r"(?!\w)"
                )

                if re.search(pattern, text):
                    found_skills.append(skill)
                    break

    return found_skills