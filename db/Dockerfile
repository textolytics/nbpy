FROM influxdb:latest

# Set environment variables
ENV INFLUXDB_DB=tick \
    INFLUXDB_HTTP_AUTH_ENABLED=false \
    INFLUXDB_HTTP_FLUX_ENABLED=true \
    INFLUXDB_DATA_LOG_ENABLED=true

# Copy custom configuration
COPY influxdb.conf /etc/influxdb/influxdb.conf

# Copy initialization script
COPY docker-entrypoint-initdb.d /docker-entrypoint-initdb.d

# Expose ports
EXPOSE 8086 8088

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8086/ping || exit 1

# Use default entrypoint from base image
ENTRYPOINT ["/entrypoint.sh"]
CMD ["influxd"]
