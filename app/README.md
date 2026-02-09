# Kubernetes Production API

A minimal, production-ready, stateless REST API built with FastAPI for Kubernetes deployments.

## 🏗️ Design Decisions

### Architecture
- **Stateless Design**: No local storage, sessions, or persistent state - fully compliant with 12-factor app principles
- **Configuration**: All configuration through environment variables for cloud-native flexibility
- **Single Responsibility**: Focused API with clear separation of concerns

### Technology Choices

#### FastAPI
- **Performance**: Built on Starlette and Pydantic - one of the fastest Python frameworks
- **Type Safety**: Automatic request/response validation using Python type hints
- **Documentation**: Auto-generated OpenAPI (Swagger) documentation at `/docs`
- **Async Support**: Native async/await support for high concurrency

#### Prometheus Metrics
- **Industry Standard**: De facto standard for Kubernetes monitoring
- **Custom Metrics**: Automatic tracking of request duration and counts
- **Efficient**: Minimal overhead with built-in middleware

### Production Features

#### Security
- **Non-root User**: Runs as UID 1001 (appuser) for container security
- **Minimal Attack Surface**: Slim Python image with only necessary dependencies
- **No Secrets in Code**: All sensitive config via environment variables

#### Observability
- **Health Checks**: `/health` for liveness, `/readiness` for readiness probes
- **Metrics**: `/metrics` endpoint for Prometheus scraping
- **Structured Logging**: JSON-compatible logging for log aggregation

#### Container Optimization
- **Multi-stage Build**: Smaller final image (~150MB vs 900MB+)
- **Layer Caching**: Requirements installed separately for faster rebuilds
- **Health Check**: Built-in Docker health check
- **.dockerignore**: Excludes unnecessary files from build context

## 📋 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Runtime information (env, version, hostname) |
| `/health` | GET | Liveness probe - returns `{"status": "ok"}` |
| `/readiness` | GET | Readiness probe - checks dependencies |
| `/metrics` | GET | Prometheus metrics endpoint |
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API documentation (ReDoc) |

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Or with custom environment
APP_ENV=development APP_VERSION=1.0.0 python main.py
```

### Docker Build & Run

```bash
# Build the image
docker build -t production-api:1.0.0 .

# Run the container
docker run -p 8080:8080 \
  -e APP_ENV=production \
  -e APP_VERSION=1.0.0 \
  production-api:1.0.0
```

### Test the API

```bash
# Health check
curl http://localhost:8080/health

# Root endpoint
curl http://localhost:8080/

# Metrics
curl http://localhost:8080/metrics
```

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment name (dev/stage/prod) |
| `APP_VERSION` | `1.0.0` | Application version |
| `PORT` | `8080` | Server port |
| `LOG_LEVEL` | `info` | Logging level (debug/info/warning/error) |

## 📊 Monitoring

The `/metrics` endpoint exposes:
- `http_requests_total` - Counter of all HTTP requests (by method, endpoint, status)
- `http_request_duration_seconds` - Histogram of request durations

Example Prometheus scrape config:
```yaml
scrape_configs:
  - job_name: 'production-api'
    scrape_interval: 15s
    static_configs:
      - targets: ['production-api:8080']
```

## 🔐 Security Considerations

1. **Non-root User**: Container runs as UID 1001
2. **Minimal Base Image**: Uses python:3.11-slim
3. **No Hardcoded Secrets**: All config via environment variables
4. **Health Checks**: Fast-failing health endpoints for quick recovery
5. **CORS**: Configure CORS middleware if needed for browser clients

## 📈 Scalability

This application is designed for horizontal scaling in Kubernetes:
- **Stateless**: No session state - any pod can handle any request
- **Single Worker**: Kubernetes handles replica scaling
- **Fast Startup**: ~1-2 seconds for pod initialization
- **Graceful Shutdown**: Proper signal handling for zero-downtime deployments

## 🛠️ Production Checklist

- [ ] Configure resource limits in Kubernetes manifests
- [ ] Set up HPA (Horizontal Pod Autoscaler) based on CPU/memory
- [ ] Configure liveness and readiness probes
- [ ] Set up Prometheus monitoring and alerting
- [ ] Configure logging aggregation (ELK, Loki, etc.)
- [ ] Implement proper CORS policies if needed
- [ ] Add authentication/authorization if required
- [ ] Set up rate limiting for public endpoints
- [ ] Configure TLS/HTTPS at ingress level

## 📝 Next Steps

To extend this API:
1. Add database connectivity (PostgreSQL, MongoDB, etc.)
2. Implement caching layer (Redis, Memcached)
3. Add authentication (JWT, OAuth2)
4. Implement rate limiting
5. Add request tracing (OpenTelemetry)
6. Set up CI/CD pipeline
