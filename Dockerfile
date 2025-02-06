FROM postgres:15.0 AS dumper
COPY id_sequence.sql /docker-entrypoint.initdb.d/id_sequence.sql
COPY enable_vector.sql /docker-entrypoint.initdb.d/enable_vector.sql
RUN ["sed", "-i", "s/exec \"$@\"/echo \"skipping...\"/", "/usr/local/bin/docker-entrypoint.sh"]
RUN apt-get update \
    && apt-get install -y lsb-release wget sudo clang-11 \
    && sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add - \
    && apt-get update \
    && apt-get install -y git build-essential postgresql-server-dev-15 \
    && git clone https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install
ENV POSTGRES_HOST_AUTH_METHOD=md5 \
    PGDATA=/data
RUN ["/usr/local/bin/docker-entrypoint.sh", "postgres"]
FROM postgres:15.0
COPY --from=dumper /data $PGDATA
COPY --from=dumper /usr/lib/postgresql/15/lib/vector.so /usr/lib/postgresql/15/lib/
COPY --from=dumper /usr/share/postgresql/15/extension/vector* /usr/share/postgresql/15/extension/