import sqlite3
from pathlib import Path
from typing import Any, Union

from src.net.profile import Profile
from src.components import Singleton

ROOT_PATH = Path(__file__).parent


class ProfileHandler(metaclass=Singleton):
    """
    A class for handling profiles and client activities.
    Note:
        Keeps track of all profiles created for a single client by mapping the hash of the ip to the profile itself.
    """
    __db_path = ROOT_PATH / "profiles_db" / "database.db"

    def __init__(self):
        conn = sqlite3.connect(ProfileHandler.__db_path)
        conn.cursor().execute("""
            CREATE TABLE IF NOT EXISTS profiles (ip_hash BLOB PRIMARY KEY, profile_object BLOB)
        """)
        self.conn = conn
        self.cursor = self.conn.cursor()

    def insert_profile(self, ip_hash: bytes, profile: Profile):
        """
        Inserts a profile mapped by the hash into the db.
        :param ip_hash: str
        :param profile:
        :return:
        """
        params = (ip_hash, profile.serialize())
        self.cursor.execute("INSERT OR IGNORE INTO profiles VALUES(?, ?)", params)

    def get_profile_by_hash(self, ip_hash: bytes) -> Union[Profile, None]:
        """
        Fetches the profile attached to the ip hash.
        :param ip_hash:
        :return:
        """
        self.cursor.execute("SELECT profile_object FROM profiles WHERE ip_hash=?", (ip_hash,))
        profile = self.cursor.fetchone()
        if profile is not None:
            return Profile.deserialize(profile[0])
        return None

    def delete_profile(self, ip_hash: bytes):
        """
        Deletes a specific profile from the db.
        :param ip_hash:
        :return:
        """
        self.cursor.execute("DELETE FROM profiles WHERE ip_hash=?", (ip_hash,))

    def update_profile(self, ip_hash: bytes, kwargs: dict):
        """
        Updates a profile with kwargs, where kwargs holds fields and values.
        :param ip_hash:
        :param kwargs:
        :return:
        """
        profile: Profile = self.get_profile_by_hash(ip_hash)
        profile.update(kwargs)
        updated_row = (profile.serialize(), ip_hash)
        self.cursor.execute("UPDATE profiles SET profile_object=? WHERE ip_hash=?", updated_row)

    def get_all_profiles(self) -> dict[bytes, Profile]:
        """
        Creates a dictionary of all profiles in the database.
        :return: dict of profiles.
        """
        self.cursor.execute("SELECT * FROM profiles")
        return {ip_hash: Profile.deserialize(profile) for ip_hash, profile in self.cursor.fetchall()}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
