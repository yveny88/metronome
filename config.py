import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_db_path() -> str:
    """Return the path to the SQLite database."""
    env_path = os.environ.get("DB_PATH")
    if env_path:
        return env_path
    docker_path = os.path.join('/app/data', 'metronome.db')
    if os.path.exists(docker_path):
        return docker_path
    return os.path.join(ROOT_DIR, 'metronome.db')


def get_sqlalchemy_uri() -> str:
    """Return SQLAlchemy URI for the SQLite database."""
    return f"sqlite:///{get_db_path()}"
