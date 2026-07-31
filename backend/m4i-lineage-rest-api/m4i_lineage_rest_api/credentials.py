import os

credentials = {
    "atlas.credentials.username": os.getenv("atlas_username", "atlas"),
    "atlas.credentials.password": os.getenv("atlas_password", "admin"),
}
