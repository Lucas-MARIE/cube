# ============================================================
# Cube.com API Gateway - Dockerfile
# Lightweight Nginx reverse proxy for routing API requests.
# ============================================================

FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom gateway configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose the gateway port
EXPOSE 8080

# Run Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
