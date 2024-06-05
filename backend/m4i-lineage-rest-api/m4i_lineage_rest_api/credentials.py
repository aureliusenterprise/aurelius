import os

credentials = {
    "atlas.credentials.username": os.getenv('atlas_username', 'admin'),
    "atlas.credentials.password": os.getenv('atlas_password', 'admin')
}
