from pathlib import Path
from src.components import Singleton


def abs_node_path(node: str, *other_nodes) -> Path:
    """
    Computes the absolute path of node (based on this root dir) joining each given node.
    :returns: absolute path
    """
    this_root = Path(__file__).parent
    for n in other_nodes: 
        this_root = this_root.joinpath(n)
    absolute_path = this_root.joinpath(node)
    return absolute_path


class SignaturesDB(metaclass=Singleton):
    def __init__(self, root_folder: str="") -> None:    
        self.sql_data_set: set = {}
        self.xss_data_set: set = {}
        self.unauthorized_access_data_set: set = {}
        self.__root_dir: Path = abs_node_path(root_folder)
    
    @staticmethod
    def __determine_if_signature(sig: str) -> bool:
        return bool(sig and not sig.strip().startswith("#"))

    def __load_signatures_from(self, source_file: str) -> set:
        """
        Loads data from `source_file`.
        :returns: Set containing all signatures.
        """
        try:
            absolute_path = self.__root_dir.joinpath(source_file)
            with open(absolute_path, "r") as data_file:
                data = set([line.strip() for line in data_file.readlines()])
                return set(filter(self.__determine_if_signature, data))
            
        except FileNotFoundError as _e:
            return set([])
        
    def load_data_sets(self) -> None:
        try:
            self.sql_data_set = self.__load_signatures_from("sql_data.txt")
            self.xss_data_set = self.__load_signatures_from("xss_data.txt")
            self.unauthorized_access_data_set = self.__load_signatures_from("unauthorized_access.txt")
        except Exception as _failed_data_sets_loading_err:
            pass


def initialize_database_instance() -> None:
    """
    Initializes database singleton instance.
    :returns: None
    """
    try:
        signatures_db: SignaturesDB = SignaturesDB(root_folder="signatures")
        signatures_db.load_data_sets()
    except Exception as _database_loading_err:
        print("ERROR: Could not initialize signatures DB due:", _database_loading_err)
