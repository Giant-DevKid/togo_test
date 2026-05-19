import random
import string


def generate_booking_id():

    prefix = "RID"

    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    return f"{prefix}-{random_part}"
