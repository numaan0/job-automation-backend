# app/tools/skill_matcher.py

from langchain_core.tools import tool
import json
import re

# ----------------------------------------------
# 1. Your constant skill list (editable later)
# ----------------------------------------------
CONSTANT_SKILLS = [
    "python",
    "django",
    "flask",
    "rest api",
    "postgresql",
    "aws",
    "docker",
    "javascript",
    "react",
    "angular",
    "git"
]

@tool
def match_skills(job_description: str) -> str:
    """
    Matches job description against a constant skill list.
    
    Returns structured JSON:
    {
        "matched": [...],
        "missing": [...],
        "match_score": 87
    }
    """

    try:
        # ----------------------------------------------
        # 2. Normalize job description for matching
        # ----------------------------------------------
        text = job_description.lower()

        matched = []
        missing = []

        # ----------------------------------------------
        # 3. Check each constant skill
        # ----------------------------------------------
        for skill in CONSTANT_SKILLS:
            # Use regex to avoid substring false matches
            pattern = r"\b" + re.escape(skill) + r"\b"

            if re.search(pattern, text):
                matched.append(skill)
            else:
                missing.append(skill)

        # ----------------------------------------------
        # 4. Match score (simple % match)
        # ----------------------------------------------
        score = int((len(matched) / len(CONSTANT_SKILLS)) * 100)

        # ----------------------------------------------
        # 5. Return structured JSON only
        # ----------------------------------------------
        return json.dumps({
            "matched": matched,
            "missing": missing,
            "match_score": score
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e)
        })
