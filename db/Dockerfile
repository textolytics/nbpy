FROM influxdb:2.7-alpine

# Set environment variables for InfluxDB 2.x
ENV INFLUXDB_INIT_MODE=setup \
    INFLUXDB_INIT_USERNAME=admin \
    INFLUXDB_INIT_PASSWORD=adminpassword \
    INFLUXDB_INIT_ORG=nbpy \
    INFLUXDB_INIT_BUCKET=tick \
    INFLUXDB_INIT_RETENTION=30d \
    INFLUXDB_INIT_ADMIN_TOKEN=zmq-admin-token-secret \
    INFLUXDB_UI_ENABLED=true

# Expose ports
# 8086: HTTP API and UI
# 8088: RPC service for backups and restore
EXPOSE 8086 8088

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8086/health || exit 1

# Use default entrypoint from base image
ENTRYPOINT ["/entrypoint.sh"]
CMD ["influxd"]
