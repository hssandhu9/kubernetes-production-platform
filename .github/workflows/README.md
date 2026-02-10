# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for the Kubernetes production platform.

## Workflows

### ci-cd.yaml
Main CI/CD pipeline for building, testing, and deploying the application to Kubernetes.

## Setup Instructions

### 1. Required GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

#### Docker Registry
- `DOCKER_USERNAME` - Docker Hub username (or registry username)
- `DOCKER_PASSWORD` - Docker Hub password or access token

#### Kubernetes Access (per environment)
- `KUBE_CONFIG_DEV` - Base64-encoded kubeconfig for dev cluster
- `KUBE_CONFIG_STAGE` - Base64-encoded kubeconfig for staging cluster
- `KUBE_CONFIG_PROD` - Base64-encoded kubeconfig for production cluster

### 2. Generate Kubeconfig Secrets

```bash
# For each cluster, get kubeconfig and encode it
kubectl config view --minify --flatten | base64 -w 0

# Or if you have separate kubeconfig files:
cat ~/.kube/config-dev | base64 -w 0
cat ~/.kube/config-stage | base64 -w 0
cat ~/.kube/config-prod | base64 -w 0
```

Copy the base64 output and add it to GitHub Secrets.

### 3. Alternative: Service Account Token Method

If you prefer using service accounts instead of full kubeconfig:

```bash
# Create service account for GitHub Actions
kubectl create serviceaccount github-actions -n kube-system

# Create ClusterRoleBinding
kubectl create clusterrolebinding github-actions-admin \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:github-actions

# Get token (Kubernetes 1.24+)
kubectl create token github-actions -n kube-system --duration=87600h

# Or for older versions:
kubectl get secret $(kubectl get sa github-actions -n kube-system -o jsonpath='{.secrets[0].name}') \
  -n kube-system -o jsonpath='{.data.token}' | base64 -d

# Get cluster info
kubectl cluster-info
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'
kubectl config view --minify --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}'
```

Then create a kubeconfig file:
```yaml
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority-data: <CA_DATA>
    server: <CLUSTER_URL>
  name: production-cluster
contexts:
- context:
    cluster: production-cluster
    user: github-actions
  name: github-actions-context
current-context: github-actions-context
users:
- name: github-actions
  user:
    token: <SERVICE_ACCOUNT_TOKEN>
```

### 4. GitHub Environments

Configure environments in GitHub (Settings → Environments):

#### development
- No protection rules (auto-deploy)
- URL: https://sample-app-dev.example.com

#### staging
- Optional: Required reviewers
- URL: https://sample-app-stage.example.com

#### production
- **Required**: At least 1 required reviewer
- Optional: Wait timer (e.g., 5 minutes)
- URL: https://sample-app.example.com

## Deployment Workflow

### Development (`develop` branch)
```bash
git checkout develop
git push origin develop
```
→ Automatically deploys to dev environment

### Staging (`main` branch)
```bash
git checkout main
git merge develop
git push origin main
```
→ Automatically deploys to staging environment

### Production (Git tags)
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```
→ Deploys to production (requires approval if configured)

## Workflow Triggers

| Trigger | Environment | Image Tag |
|---------|-------------|-----------|
| Push to `develop` | Development | `:dev` |
| Push to `main` | Staging | `:stage` |
| Tag `v*` | Production | `:v1.0.0` (tag name) |
| Pull Request | None (test only) | N/A |

## Manual Rollback

To rollback production deployment:

1. Go to Actions → Rollback Production workflow
2. Click "Run workflow"
3. Confirm the rollback

Or use kubectl directly:
```bash
kubectl rollout undo deployment/sample-app -n prod
```

## Customization

### Use Different Container Registry

Update in `.github/workflows/ci-cd.yaml`:

```yaml
env:
  REGISTRY: ghcr.io  # GitHub Container Registry
  # or
  REGISTRY: gcr.io   # Google Container Registry
  # or
  REGISTRY: <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com  # AWS ECR
```

For GHCR:
```yaml
- name: Log in to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Add Tests

Uncomment and customize the test step:
```yaml
- name: Run tests
  run: |
    cd app
    pytest tests/ --cov=. --cov-report=xml
```

### Add Smoke Tests

Update the production deployment smoke tests:
```yaml
- name: Run smoke tests
  run: |
    curl -f https://sample-app.example.com/health || exit 1
    curl -f https://sample-app.example.com/ || exit 1
```

## Monitoring Deployments

### View deployment status
```bash
# Watch rollout status
kubectl rollout status deployment/sample-app -n prod

# Check pods
kubectl get pods -n prod -l app=sample-app

# Check recent events
kubectl get events -n prod --sort-by='.lastTimestamp'

# View logs
kubectl logs -n prod -l app=sample-app --tail=100 -f
```

## Troubleshooting

### Deployment stuck in "Progressing"
```bash
kubectl describe deployment sample-app -n prod
kubectl get pods -n prod -l app=sample-app
kubectl logs -n prod <pod-name>
```

### Image pull errors
- Verify Docker registry credentials
- Check image exists: `docker pull <image>`
- Verify image pull secrets if using private registry

### Permission errors
- Verify kubeconfig has necessary permissions
- Check service account has cluster-admin or necessary RBAC roles

### Rollout taking too long
- Check resource limits
- Verify health check endpoints are responding
- Check HPA metrics

## Security Best Practices

1. ✅ Use service accounts with minimal permissions
2. ✅ Rotate credentials regularly
3. ✅ Use environment protection rules for production
4. ✅ Never commit secrets to git
5. ✅ Use short-lived tokens when possible
6. ✅ Audit deployment logs regularly
7. ✅ Enable branch protection on `main` and `develop`
