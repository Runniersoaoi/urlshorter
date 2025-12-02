from hashids import Hashids
import os

SALT = os.getenv("HASHIDS_SALT", "my-secret-salt")
MIN_LENGTH = 6

hashids = Hashids(salt=SALT, min_length=MIN_LENGTH)

def generate_short_id(db_id: int) -> str:
    return hashids.encode(db_id)
