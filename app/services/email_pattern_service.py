import re
from typing import List

class EmailPatternService:

    @staticmethod
    def normalize_name(name: str):
        """
        Clean 'Rohit Sharma' → ('rohit', 'sharma')
        """
        name = name.strip().lower()
        parts = re.split(r"\s+", name)

        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[-1]

    @staticmethod
    def generate_patterns(first: str, last: str, domain: str) -> List[str]:
        """
        Generate all common corporate email patterns.
        """

        f = first[0] if first else ""
        l = last[0] if last else ""

        patterns = [
            f"{first}@{domain}",
            f"{last}@{domain}",
            f"{first}{last}@{domain}",
            f"{first}.{last}@{domain}",
            f"{first}_{last}@{domain}",
            f"{first}-{last}@{domain}",
            f"{first}{l}@{domain}",
            f"{first}.{l}@{domain}",
            f"{f}{last}@{domain}",
            f"{f}.{last}@{domain}",
            f"{f}{l}@{domain}",
            f"{first}{last}{l}@{domain}",
            f"{last}{first}@{domain}",
        ]

        # Remove duplicates and empty ones
        return sorted(list({email for email in patterns if "@" in email}))
