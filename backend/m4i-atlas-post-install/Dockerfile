FROM aureliusatlas/docker-flink:2.0.1

USER root

RUN apt-get update
RUN apt-get install -y jq curl

USER flink

COPY ./backend/m4i-atlas-post-install/requirements.txt ./

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY ./backend/m4i-atlas-post-install/m4i_atlas_post_install/* ./

# todo referenced
# todo remove image stuff

#CMD ["./run.sh"]
CMD ["echo asd && tail -f /dev/null"]
