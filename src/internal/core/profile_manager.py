import sqlite3
from pathlib import Path
from typing import Union

from src.internal.core.profile import Profile
from src.components import Singleton

ROOT_PATH = Path(__file__).parent


class ProfileManager(metaclass=Singleton):
    """
    A class for handling profiles and client activities.
    """
    __db_path = ROOT_PATH / "profiles_db" / "database.db"

    def __init__(self):
        conn = sqlite3.connect(ProfileManager.__db_path)
        conn.cursor().execute("""
            CREATE TABLE IF NOT EXISTS profiles (ip_hash TEXT PRIMARY KEY, profile_object BLOB)
        """)
        self.conn = conn
        self.cursor = self.conn.cursor()

    def insert_profile(self, client_hash: str, profile: Profile):
        """
        Inserts a profile mapped by the hash into the db.
        :param client_hash: str
        :param profile:
        :return:
        """
        params = (client_hash, profile.serialize())
        self.cursor.execute("INSERT OR IGNORE INTO profiles VALUES(?, ?)", params)

    def get_profile_by_hash(self, client_hash: str) -> Union[Profile, None]:
        """
        Fetches the profile attached to the ip hash.
        :param client_hash:
        :return:
        """
        self.cursor.execute("SELECT profile_object FROM profiles WHERE ip_hash=?", (client_hash,))
        profile = self.cursor.fetchone()
        if profile is not None:
            return Profile.deserialize(profile[0])
        return None

    def delete_profile(self, client_hash: str):
        """
        Deletes a specific profile from the db.
        :param client_hash:
        :return:
        """
        self.cursor.execute("DELETE FROM profiles WHERE ip_hash=?", (client_hash,))

    def update_profile(self, client_hash: str, kwargs: dict):
        """
        Updates a profile with kwargs, where kwargs holds fields and values.
        :param client_hash:
        :param kwargs:
        :return:
        """
        profile: Profile = self.get_profile_by_hash(client_hash)
        profile.update(kwargs)
        updated_row = (profile.serialize(), client_hash)
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
