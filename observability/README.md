# Observability Stack

Complete observability solution for the Kubernetes production platform with metrics, logs, and alerts.

## Components

### 📊 Prometheus
- **Purpose**: Metrics collection and storage
- **Port**: 9090
- **Features**:
  - Auto-discovery of Kubernetes services and pods
  - Custom alerting rules
  - 30-day retention
  - Scrapes metrics from annotated pods

### 📈 Grafana
- **Purpose**: Visualization and dashboards
- **Port**: 3000
- **Default Credentials**: 
  - Username: `admin`
  - Password: `admin123` (⚠️ Change in production!)
- **Pre-configured Dashboards**:
  - Application Metrics (Request rate, errors, latency)
  - Kubernetes Cluster Metrics (CPU, memory, pod restarts)
- **Data Sources**:
  - Prometheus (metrics)
  - Loki (logs)

### 📝 Loki
- **Purpose**: Log aggregation and storage
- **Port**: 3100
- **Features**:
  - 31-day log retention
  - Indexed by labels (namespace, pod, container)
  - Integrated with Grafana for log exploration

### 🚚 Promtail
- **Purpose**: Log collection agent
- **Deployment**: DaemonSet (runs on every node)
- **Features**:
  - Collects logs from all pods
  - Parses container logs (CRI format)
  - Extracts structured data from JSON logs
  - Adds Kubernetes metadata

### 🔔 AlertManager
- **Purpose**: Alert routing and notification
- **Port**: 9093
- **Features**:
  - Groups similar alerts
  - Deduplication
  - Inhibition rules (suppress warnings when critical alerts fire)
  - Webhook receivers (configure Slack, PagerDuty, etc.)

## Deployment

### Quick Start

```bash
# Deploy entire observability stack
kubectl apply -k observability/

# Verify deployment
kubectl get pods -n observability

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=observability-stack -n observability --timeout=300s
```

### Access the Services

#### Port Forwarding (Development)

```bash
# Grafana
kubectl port-forward -n observability svc/grafana 3000:3000

# Prometheus
kubectl port-forward -n observability svc/prometheus 9090:9090

# AlertManager
kubectl port-forward -n observability svc/alertmanager 9093:9093

# Loki
kubectl port-forward -n observability svc/loki 3100:3100
```

Then access:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- AlertManager: http://localhost:9093
- Loki: http://localhost:3100

## Application Integration

### Enable Metrics Scraping

Add these annotations to your application's Pod spec to enable Prometheus scraping:

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

Your FastAPI application already exposes metrics at `/metrics` endpoint!

### Example for the Sample App

Update `manifests/base/deployment.yaml`:

```yaml
spec:
  template:
    metadata:
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
      labels:
        app: sample-app
```

## Alert Rules

### Pre-configured Alerts

1. **HighErrorRate**: Triggers when error rate > 5% for 5 minutes
2. **HighLatency**: Triggers when 95th percentile latency > 1s for 5 minutes
3. **PodCrashLooping**: Pod has restarted multiple times
4. **PodNotReady**: Pod not in Ready state for 10+ minutes
5. **HighMemoryUsage**: Memory usage > 90% for 5 minutes
6. **HighCPUUsage**: CPU usage > 90% for 5 minutes

### Customize Alerts

Edit [prometheus-rules.yaml](prometheus-rules.yaml) to add or modify alert rules.

### Configure Notifications

Edit [alertmanager-config.yaml](alertmanager-config.yaml) to configure notification channels:

#### Slack Example
```yaml
receivers:
  - name: 'critical'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts-critical'
        title: 'Critical Alert: {{ .GroupLabels.alertname }}'
```

#### Email Example
```yaml
receivers:
  - name: 'warning'
    email_configs:
      - to: 'team@example.com'
        from: 'alertmanager@example.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alertmanager@example.com'
        auth_password: 'your-app-password'
```

## Querying Logs

### Using Grafana Explore

1. Open Grafana → Explore
2. Select "Loki" data source
3. Use LogQL queries:

```logql
# All logs from sample-app
{app="sample-app"}

# Error logs only
{app="sample-app"} |= "error"

# Logs with specific status code
{app="sample-app"} | json | status="500"

# Rate of error logs
rate({app="sample-app"} |= "error" [5m])
```

## Monitoring Dashboards

### Application Dashboard
- Request rate per endpoint
- Error rate trends
- P95 latency
- HTTP status code distribution

### Kubernetes Dashboard
- CPU usage per pod
- Memory usage per pod
- Pod restart count
- Node resource utilization

### Custom Dashboards

Create custom dashboards in Grafana:
1. Login to Grafana
2. Click "+" → "Dashboard"
3. Add Panel → Choose visualization
4. Write PromQL queries for metrics
5. Save dashboard

## Metrics Examples

### Query Prometheus

```promql
# Total request rate
sum(rate(http_requests_total[5m]))

# Error rate by endpoint
sum(rate(http_requests_total{status=~"5.."}[5m])) by (endpoint)

# P95 latency
histogram_quantile(0.95, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)

# Memory usage
sum(container_memory_usage_bytes{pod=~"sample-app.*"})
```

## Production Considerations

### Storage
The current setup uses `emptyDir` volumes (ephemeral). For production:

1. **Prometheus**: Use PersistentVolumeClaim for metrics
2. **Loki**: Use S3/GCS for chunks storage
3. **Grafana**: Use PersistentVolumeClaim or external database

### High Availability
- Run multiple replicas of Prometheus (with Thanos for global view)
- Configure Loki in microservices mode
- Use external AlertManager clustering

### Security
- Change Grafana default password
- Enable authentication for Prometheus and AlertManager
- Use TLS for all services
- Implement network policies

### Resource Tuning
Adjust resource limits based on your cluster size:
- Prometheus: Increase memory for larger clusters
- Loki: Adjust retention based on log volume
- Promtail: Monitor node resource usage

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n observability
kubectl describe pod <pod-name> -n observability
kubectl logs <pod-name> -n observability
```

### Verify Service Discovery
```bash
# Check Prometheus targets
kubectl port-forward -n observability svc/prometheus 9090:9090
# Open http://localhost:9090/targets
```

### Test Loki Ingestion
```bash
# Check if Promtail is sending logs
kubectl logs -n observability -l app=promtail
```

### Debug Alerts
```bash
# Check AlertManager status
kubectl port-forward -n observability svc/alertmanager 9093:9093
# Open http://localhost:9093
```

## Cleanup

```bash
# Remove entire observability stack
kubectl delete -k observability/

# Or delete namespace (removes everything)
kubectl delete namespace observability
```

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [LogQL Guide](https://grafana.com/docs/loki/latest/logql/)

## Support

For issues or questions:
1. Check pod logs: `kubectl logs -n observability <pod-name>`
2. Review configurations in ConfigMaps
3. Verify RBAC permissions
4. Check resource availability on nodes
