def first_name_from(value: str) -> str:
    if not value:
        return ""
    parts = str(value).strip().split()
    return parts[0] if parts else ""


def build_message_context(lead: dict) -> dict:
    full_name = lead.get("full_name") or lead.get("name") or ""
    headline = lead.get("headline") or ""
    profile_location = lead.get("profile_location") or ""
    location = lead.get("location") or profile_location
    current_title = lead.get("current_title") or ""
    companies = lead.get("companies") or ""
    if isinstance(companies, list):
        companies = ", ".join([c for c in companies if c])
    companies = companies or ""
    company = ""
    if isinstance(companies, str) and companies:
        company = companies.split(",")[0].strip()

    public_identifier = lead.get("linkedin_public_id") or lead.get("public_identifier") or ""
    provider_id = lead.get("provider_id") or lead.get("id") or ""
    profile_url = ""
    if public_identifier:
        profile_url = f"https://www.linkedin.com/in/{public_identifier}"

    context = {
        "first_name": first_name_from(full_name),
        "full_name": full_name,
        "headline": headline,
        "location": location or "",
        "profile_location": profile_location or "",
        "current_title": current_title or "",
        "companies": companies,
        "company": company,
        "company_id": lead.get("company_id") or "",
        "bio": lead.get("bio") or "",
        "public_identifier": public_identifier,
        "provider_id": provider_id,
        "profile_url": profile_url,
    }
    for key, value in lead.items():
        if key not in context:
            context[key] = value if value is not None else ""
    return context


class SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


def render_message(template: str, lead: dict) -> str:
    context = build_message_context(lead)
    try:
        return template.format_map(SafeFormatDict(context))
    except Exception:
        return template
