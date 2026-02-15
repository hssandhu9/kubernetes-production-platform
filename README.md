# Kubernetes Production Platform

A complete, production-ready Kubernetes deployment platform featuring a FastAPI application with enterprise-grade observability, multi-environment support, and GitOps-ready manifests.

## 🎯 Overview

This project demonstrates a modern, cloud-native application deployment on Kubernetes with:

- **Production-ready FastAPI application** with built-in metrics and health checks
- **Multi-environment manifests** using Kustomize (dev, stage, prod)
- **Complete observability stack** with Prometheus, Grafana, Loki, and AlertManager
- **GitOps-ready** with declarative Kubernetes manifests
- **Security-first** with non-root containers, resource limits, and RBAC
- **Auto-scaling** with Horizontal Pod Autoscaler (HPA)

## 📁 Project Structure

```
kubernetes-production-platform/
├── app/                          # FastAPI application
│   ├── main.py                   # Application code with metrics
│   ├── Dockerfile                # Multi-stage container build
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Application documentation
├── manifests/                    # Kubernetes manifests
│   ├── base/                     # Base configurations (Kustomize)
│   │   ├── deployment.yaml       # Application deployment
│   │   ├── service.yaml          # Service definition
│   │   ├── ingress.yaml          # Ingress configuration
│   │   ├── hpa.yaml              # Horizontal Pod Autoscaler
│   │   ├── configmap.yaml        # Configuration management
│   │   ├── secret.yaml           # Secrets (example)
│   │   └── kustomization.yaml    # Kustomize base
│   └── overlays/                 # Environment-specific configs
│       ├── dev/                  # Development environment
│       ├── stage/                # Staging environment
│       └── prod/                 # Production environment
├── observability/                # Complete monitoring stack
│   ├── prometheus-*.yaml         # Metrics collection & alerting
│   ├── grafana-*.yaml            # Visualization & dashboards
│   ├── loki-*.yaml               # Log aggregation
│   ├── promtail-*.yaml           # Log collection
│   ├── alertmanager-*.yaml       # Alert routing
│   └── README.md                 # Observability documentation
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured
- Docker (for building images)
- Optional: kustomize (built into kubectl 1.14+)

### 1. Build and Push the Application

```bash
# Build the Docker image
cd app
docker build -t sample-app:latest .

# Tag and push to your registry (replace with your registry)
docker tag sample-app:latest your-registry/sample-app:latest
docker push your-registry/sample-app:latest
```

### 2. Deploy the Application

```bash
# Deploy to development environment
kubectl apply -k manifests/overlays/dev/

# Or staging
kubectl apply -k manifests/overlays/stage/

# Or production
kubectl apply -k manifests/overlays/prod/
```

### 3. Deploy Observability Stack

```bash
# Deploy complete monitoring stack
kubectl apply -k observability/

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=observability-stack -n observability --timeout=300s
```

### 4. Access the Application

```bash
# Port forward the application
kubectl port-forward -n dev svc/sample-app 8080:8080

# Test the API
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/metrics
```

### 5. Access Monitoring Dashboards

```bash
# Grafana (username: admin, password: admin123)
kubectl port-forward -n observability svc/grafana 3000:3000
# Open: http://localhost:3000

# Prometheus
kubectl port-forward -n observability svc/prometheus 9090:9090
# Open: http://localhost:9090

# AlertManager
kubectl port-forward -n observability svc/alertmanager 9093:9093
# Open: http://localhost:9093
```

## 🏗️ Architecture

### Application Layer

The FastAPI application is designed with cloud-native principles:

- **Stateless**: No local storage, fully horizontal scalable
- **12-Factor App**: Configuration via environment variables
- **Health Checks**: Liveness and readiness probes
- **Metrics**: Prometheus metrics at `/metrics` endpoint
- **Security**: Runs as non-root user (UID 1001)
- **Performance**: Async support for high concurrency

### Kubernetes Resources

#### Base Resources
- **Deployment**: Application pods with resource limits and security context
- **Service**: ClusterIP service for internal communication
- **Ingress**: HTTP routing with TLS support
- **HPA**: Auto-scaling based on CPU/memory (2-10 replicas)
- **ConfigMap**: Environment-specific configuration
- **Secret**: Sensitive data (passwords, tokens)

#### Environment Overlays
Each environment (dev/stage/prod) can override:
- Replica counts
- Resource limits
- Environment variables
- Ingress hostnames
- Scaling thresholds

### Observability Stack

Complete monitoring solution with:

| Component | Purpose | Port |
|-----------|---------|------|
| **Prometheus** | Metrics collection & storage | 9090 |
| **Grafana** | Visualization & dashboards | 3000 |
| **Loki** | Log aggregation | 3100 |
| **Promtail** | Log collection (DaemonSet) | 9080 |
| **AlertManager** | Alert routing & notification | 9093 |

**Pre-configured Features:**
- Auto-discovery of Kubernetes services
- Application metrics dashboards
- Kubernetes cluster dashboards
- Alert rules (error rate, latency, pod health)
- 30-day metrics retention
- 31-day log retention

## 📊 Monitoring & Alerts

### Metrics Available

The application exposes Prometheus metrics:

```promql
# Total HTTP requests
http_requests_total{method="GET", endpoint="/", status="200"}

# Request duration histogram
http_request_duration_seconds_bucket{method="GET", endpoint="/"}
```

### Pre-configured Alert Rules

- **HighErrorRate**: Error rate > 5% for 5 minutes
- **HighLatency**: P95 latency > 1s for 5 minutes
- **PodCrashLooping**: Pod restarting frequently
- **PodNotReady**: Pod not ready for 10+ minutes
- **HighMemoryUsage**: Memory > 90% for 5 minutes
- **HighCPUUsage**: CPU > 90% for 5 minutes

### Custom Dashboards

Two Grafana dashboards are pre-configured:
1. **Application Metrics**: Request rate, errors, latency
2. **Kubernetes Cluster**: CPU, memory, pod restarts

## 🔧 Configuration

### Application Configuration

Environment variables (via ConfigMap):

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Environment name | `development` |
| `APP_VERSION` | Application version | `1.0.0` |
| `LOG_LEVEL` | Logging level | `info` |
| `PORT` | HTTP server port | `8080` |

### Kubernetes Configuration

Edit manifests for your needs:

```bash
# Update image in base/kustomization.yaml
images:
- name: sample-app
  newName: your-registry/sample-app
  newTag: v1.2.3

# Customize resources in overlays
# Example: prod/patch.yaml
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: sample-app
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
```

### Observability Configuration

**Change Grafana Password:**
Edit `observability/grafana-deployment.yaml`:
```yaml
stringData:
  admin-password: "your-secure-password"
```

**Configure Alert Notifications:**
Edit `observability/alertmanager-config.yaml` to add Slack, email, or PagerDuty:
```yaml
receivers:
  - name: 'critical'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
```

## 🛡️ Security Features

### Container Security
- ✅ Runs as non-root user (UID 1001)
- ✅ Read-only root filesystem capable
- ✅ No privileged escalation
- ✅ Security context with fsGroup
- ✅ Minimal base image (Python slim)

### Kubernetes Security
- ✅ Resource limits prevent resource exhaustion
- ✅ Secrets for sensitive data
- ✅ RBAC for service accounts (Prometheus, Promtail)
- ✅ Network policies ready (add as needed)
- ✅ Pod Security Standards compliant

### Production Checklist
- [ ] Change default Grafana password
- [ ] Use real TLS certificates for Ingress
- [ ] Configure actual secret values (not examples)
- [ ] Set up persistent storage for metrics/logs
- [ ] Configure alert notification channels
- [ ] Implement network policies
- [ ] Set up backup strategy
- [ ] Configure image pull secrets for private registry

## 📈 Scaling

### Horizontal Pod Autoscaler

The HPA automatically scales pods based on resource usage:

```yaml
# Default configuration
minReplicas: 2
maxReplicas: 10
targetCPUUtilizationPercentage: 70
targetMemoryUtilizationPercentage: 80
```

Monitor scaling:
```bash
kubectl get hpa -n dev
kubectl describe hpa sample-app -n dev
```

### Manual Scaling

```bash
# Scale to specific replica count
kubectl scale deployment sample-app -n dev --replicas=5

# Or edit the overlay
kubectl edit deployment sample-app -n dev
```

## 🧪 Testing

### Test Application Endpoints

```bash
# Health check
curl http://localhost:8080/health

# Readiness check
curl http://localhost:8080/readiness

# Application info
curl http://localhost:8080/

# Prometheus metrics
curl http://localhost:8080/metrics
```

### Load Testing

```bash
# Using Apache Bench
ab -n 10000 -c 100 http://localhost:8080/

# Using hey
hey -n 10000 -c 100 http://localhost:8080/
```

Watch metrics in Grafana and alerts in AlertManager!

## 🔄 CI/CD Integration

This project is GitOps-ready. Integrate with:

### ArgoCD
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: sample-app-dev
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/kubernetes-production-platform
    targetRevision: HEAD
    path: manifests/overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: dev
```

### Flux
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  name: sample-app-dev
spec:
  interval: 5m
  path: ./manifests/overlays/dev
  sourceRef:
    kind: GitRepository
    name: kubernetes-production-platform
```

### GitHub Actions
```yaml
name: Build and Deploy
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker image
        run: |
          docker build -t ${{ secrets.REGISTRY }}/sample-app:${{ github.sha }} ./app
          docker push ${{ secrets.REGISTRY }}/sample-app:${{ github.sha }}
      - name: Update Kustomize image
        run: |
          cd manifests/base
          kustomize edit set image sample-app=${{ secrets.REGISTRY }}/sample-app:${{ github.sha }}
```

## 🐛 Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods -n dev

# Describe pod for events
kubectl describe pod <pod-name> -n dev

# Check logs
kubectl logs <pod-name> -n dev
```

### Metrics Not Appearing

```bash
# Verify Prometheus targets
kubectl port-forward -n observability svc/prometheus 9090:9090
# Open http://localhost:9090/targets

# Check pod annotations
kubectl get pod <pod-name> -n dev -o yaml | grep prometheus
```

### High Resource Usage

```bash
# Check resource usage
kubectl top pods -n dev

# Check HPA status
kubectl get hpa -n dev

# Review metrics in Grafana
```

### Logs Not in Loki

```bash
# Check Promtail logs
kubectl logs -n observability -l app=promtail

# Verify Loki is receiving logs
kubectl logs -n observability -l app=loki
```

## 📚 Documentation

- [Application README](app/README.md) - Detailed app documentation
- [Observability README](observability/README.md) - Monitoring stack guide
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test in dev environment: `kubectl apply -k manifests/overlays/dev/`
5. Commit: `git commit -am 'Add my feature'`
6. Push: `git push origin feature/my-feature`
7. Create a Pull Request

## 📝 License

This project is provided as-is for educational and reference purposes.

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Prometheus](https://prometheus.io/) - Monitoring and alerting
- [Grafana](https://grafana.com/) - Observability platform
- [Loki](https://grafana.com/oss/loki/) - Log aggregation
- [Kubernetes](https://kubernetes.io/) - Container orchestration
- [Kustomize](https://kustomize.io/) - Kubernetes configuration management

## 📞 Support

For issues or questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review component-specific READMEs
- Check Kubernetes events: `kubectl get events -n <namespace>`
- Review logs: `kubectl logs -n <namespace> <pod-name>`

---

**Built with ❤️ for production Kubernetes deployments**