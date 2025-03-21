from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str
    setup_complete: bool
    database_url: str
    secret_key: str
    timezone: str
    event_begin: str
    event_end: str
    slot_interval: str
    activities: dict

    class Config:
        env_file = ".env"

def update_settings(key: str, value: str, env_file: str = ".env"):
    key = key.upper()
    global settings
    print("Changing setting: " + key + " to: " + value + "")
    # Read the current .env file
    load_dotenv(env_file)
    with open(env_file, "r") as file:
        lines = file.readlines()

    # Update or add the key-value pair
    key_exists = False
    with open(env_file, "w") as file:
        for line in lines:
            if line.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
                key_exists = True
            else:
                file.write(line)
        if not key_exists:
            exit(-1)

    # Reload the environment variables
    load_dotenv(env_file, override=True)

    # Reload the settings
    settings = Settings()
    return settings

def reload_settings(env_file: str = ".env"):
    print("reloading settings...")
    # Reload the environment variables
    load_dotenv(env_file, override=True)

    # Reload the settings
    global settings
    settings = Settings()
    print("reload successful!")
    return settings

global settings
settings = Settings()