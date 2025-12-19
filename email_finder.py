import aiodns
import asyncio
import smtplib

# ------------------------------------
# SMTP VALIDATION
# ------------------------------------
async def validate_email_smtp(email: str) -> bool:
    try:
        domain = email.split("@")[1]

        # 1. Get MX records
        resolver = aiodns.DNSResolver()
        mx_records = await resolver.query(domain, 'MX')
        mx_record = sorted(mx_records, key=lambda x: x.priority)[0].host

        # 2. Connect to mail server
        server = smtplib.SMTP(timeout=8)
        server.connect(mx_record)
        server.helo("test.com")
        server.mail("test@test.com")

        # 3. Check recipient
        code, _ = server.rcpt(email)
        server.quit()

        return code == 250  # 250 = valid
    except Exception as e:
        return False


# ------------------------------------
# TEST FUNCTION
# ------------------------------------
async def test_email_search(first, last, domain):
    patterns = [
    f"{first}@{domain}",
    f"{first}{last}@{domain}",
    f"{first}.{last}@{domain}",
    f"{first}_{last}@{domain}",
    f"{first}-{last}@{domain}",

    f"{first[0]}{last}@{domain}",
    f"{first}{last[0]}@{domain}",
    f"{first[0]}.{last}@{domain}",
    f"{first}.{last[0]}@{domain}",
    f"{first[0]}_{last}@{domain}",
    f"{first}_{last[0]}@{domain}",
    f"{first[0]}-{last}@{domain}",
    f"{first}-{last[0]}@{domain}",

    f"{last}@{domain}",
    f"{last}{first}@{domain}",
    f"{last}.{first}@{domain}",
    f"{last}_{first}@{domain}",
    f"{last}-{first}@{domain}",

    # Shortened last name versions
    f"{first}.{last[:2]}@{domain}",
    f"{first}.{last[:3]}@{domain}",
    f"{first}{last[:2]}@{domain}",
    f"{first}{last[:3]}@{domain}",

    # Initial-first variations
    f"{last[0]}.{first}@{domain}",
    f"{last[0]}{first}@{domain}",

    # Ultra-short corporate forms
    f"{first[:3]}.{last[0]}@{domain}",
    f"{first[:2]}{last[0]}@{domain}",
    f"{first[0]}{last[:2]}@{domain}",
]

    print("\n⚡ Testing Email Patterns:")
    print("--------------------------")

    for email in patterns:
        is_valid = await validate_email_smtp(email)
        result = "VALID ✅" if is_valid else "Invalid ❌"
        print(f"{email:40} {result}")

    print("--------------------------\n")


# ------------------------------------
# RUN TEST
# ------------------------------------
if __name__ == "__main__":
    # CHANGE THESE
    first = "vaibhav"
    last = "goel"
    domain = "accenture.com"

    # asyncio.run(test_email_search(first, last, domain))
    asyncio.run(test_email_search(first, last, domain))
