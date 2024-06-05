import os

config = {
     "atlas.server.url": os.getenv('atlas_server_url', "localhost:21000")
}
