"""Aurelius functionality inside pyatlas (replaces the Flink jobs and the Python back ends of Aurelius).

All routes live under ``/api/aurelius``; the reverse proxy maps the frontend's paths onto them
(``dev/pyatlas/reverse-proxy/aurelius.conf``).  Phase 1: the frontend's clickstream and error reports.
Later phases add search (App Search compatible), governance/data quality, lineage and the dashboard.
"""
