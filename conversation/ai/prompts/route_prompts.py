CREATE_ROUTE_PROMPT = """

Extract route details.

Return ONLY valid JSON.

{
    "start_name": "",
    "destination_name": ""
}

Rules:

- Use null for missing values
- Never explain
- Never add markdown

"""