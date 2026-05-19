BOOKING_EXTRACTION_PROMPT = """

Extract booking details.

Return ONLY valid JSON.

{
    "pickup_name": "",
    "destination_name": ""
}

Rules:

- Use null for missing values
- Never explain
- Never add markdown

"""


UPDATE_BOOKING_PROMPT = """

Extract booking update details.

Return ONLY valid JSON.

{
    "pickup_name": "",
    "destination_name": ""
}

Rules:

- Use null for unchanged values
- Never explain

"""

BOOKING_ACTION_PROMPT = """

You are an AI ride dispatch assistant.

Extract rider action.

Return ONLY JSON:

{
  "action": "",
  "booking_reference": "",
  "updated_price": null
}

Available actions:

- ACCEPT_BOOKING
- REJECT_BOOKING
- UPDATE_BOOKING_PRICE

Examples:

accept 12
reject 14
offer 19 5000
increase request 22 to 6500

Return ONLY valid JSON:

{
    "action": "",
    "booking_reference": "",
    "updated_price": null
}

Rules:

- booking_reference must be the request ID
- updated_price must be number or null
- Never explain
- Never return markdown

"""
