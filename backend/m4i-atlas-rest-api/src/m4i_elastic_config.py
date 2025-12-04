import os
config = {
    "elastic_username": os.getenv('elastic_username'),
    "elastic_password": os.getenv('elastic_password'),
    "elastic_host": os.getenv('elastic_host'),
    "elastic_ca_certs_path": os.getenv('elastic_ca_certs_path')
}

