import pathlib
import tomllib

from pydantic import BaseModel, SecretStr
from sqlalchemy import URL


class BackendCredentials(BaseModel):
    # Used for authentication as admin
    admin_api_key: SecretStr
    # Used for JWT Token and SessionMiddleware
    backend_secret: SecretStr


class DatabaseCredentials(BaseModel):
    username: str
    password: SecretStr
    host: str
    dbname: str

    def url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.host,
            database=self.dbname,
        )


class GoogleAuthCredentials(BaseModel):
    google_client_id: SecretStr
    google_client_secret: SecretStr


class EmailCredentials(BaseModel):
    email_address: str
    email_password: SecretStr
    hostname: str
    port: int


class Credentials(BaseModel):
    backend: BackendCredentials
    database: DatabaseCredentials
    google_auth: GoogleAuthCredentials | None = None
    email: EmailCredentials | None = None


CREDENTIALS_PATH = (
    pathlib.Path(__file__).parent.parent.parent / "credentials" / "credentials.toml"
)
with open(CREDENTIALS_PATH, "rb") as credentials_file:
    credentials = Credentials.model_validate(tomllib.load(credentials_file))

__all__ = [
    "Credentials",
]
