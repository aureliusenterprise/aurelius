import os
config = {
    "atlas.server.url":  os.getenv('atlas_server_url'),#"127.0.0.1:9100/atlas/atlas",
    "data2model.server.url": os.getenv('data2model_server_url'), #"http://localhost:5000/data2model"
}

