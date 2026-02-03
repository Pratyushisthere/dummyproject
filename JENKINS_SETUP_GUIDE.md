# Jenkins Setup Guide for Blue Reserve Project

This guide will help you configure Jenkins to successfully build and deploy the Blue Reserve application.

## Prerequisites

- Jenkins installed and running
- Podman and podman-compose installed on Jenkins agent
- Access to a container registry (Docker Hub, Quay.io, etc.)
- MongoDB Atlas cluster or MongoDB instance
- IBM SSO OAuth credentials (or your OAuth provider)

## Step 1: Install Required Jenkins Plugins

Go to **Manage Jenkins → Plugins → Available Plugins** and install:

1. **Pipeline** - For Jenkinsfile support
2. **Git** - For source code management
3. **Credentials Binding** - For secure credential handling
4. **Docker Pipeline** (optional) - For container operations

## Step 2: Configure Jenkins Credentials

All credentials must be configured before running the pipeline. Go to:
**Jenkins → Manage Jenkins → Credentials → System → Global credentials (unrestricted) → Add Credentials**

### Application Credentials (10 required)

For each credential below, select **Kind: Secret text** and use the exact **ID** shown:

| # | ID | Description | Example Value |
|---|----|-----------|--------------| 
| 1 | `mongo-url` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| 2 | `session-secret` | Session encryption key | `your-random-secret-key-min-32-chars` |
| 3 | `client-id` | OAuth Client ID | `MzA0ZWZkNDAtMDc3Yi00` |
| 4 | `client-secret` | OAuth Client Secret | `MGIzZjI3MzYtOGVlZC00` |
| 5 | `token-url` | OAuth Token Endpoint | `https://login.w3.ibm.com/v1.0/endpoint/default/token` |
| 6 | `auth-endpoint` | OAuth Authorization URL | `https://login.w3.ibm.com/v1.0/endpoint/default/authorize` |
| 7 | `jwks-url` | JWKS URL for token validation | `https://login.w3.ibm.com/v1.0/endpoint/default/jwks` |
| 8 | `jwt-issuer` | JWT Issuer identifier | `https://login.w3.ibm.com/oidc/endpoint/default` |
| 9 | `redirect-uri` | OAuth callback URL | `http://YOUR_SERVER:8000/auth/ibm/callback` |
| 10 | `frontend-url` | Frontend application URL | `http://YOUR_SERVER:8080` |

### Container Registry Credentials (2 required)

| # | ID | Kind | Description |
|---|----|----|-------------|
| 11 | `container-registry-url` | Secret text | Registry URL (e.g., `docker.io`, `quay.io`) |
| 12 | `registry-credentials` | Username with password | Registry login credentials |

### Detailed Steps to Add Each Credential:

1. Click **Add Credentials**
2. **Kind**: Select "Secret text" (or "Username with password" for registry-credentials)
3. **Scope**: Global
4. **Secret**: Paste the actual value (no quotes)
5. **ID**: Enter the exact ID from the table above (case-sensitive!)
6. **Description**: Optional, but helpful (e.g., "MongoDB Atlas Connection String")
7. Click **Create**

**Repeat for all 12 credentials.**

## Step 3: Update Jenkinsfile Configuration

Edit the `Jenkinsfile` in your repository:

```groovy
environment {
    REGISTRY_URL = credentials('container-registry-url')
    REGISTRY_CREDENTIALS = credentials('registry-credentials')
    REGISTRY_NAMESPACE = 'YOUR_REGISTRY_USERNAME'  // ⚠️ CHANGE THIS!
    
    BACKEND_IMAGE = "${REGISTRY_URL}/${REGISTRY_NAMESPACE}/blu-reserve-backend"
    FRONTEND_IMAGE = "${REGISTRY_URL}/${REGISTRY_NAMESPACE}/blu-reserve-frontend"
    
    BUILD_TAG = "${env.BUILD_NUMBER}"
}
```

**Important**: Replace `YOUR_REGISTRY_USERNAME` with your actual container registry username.

## Step 4: Create Jenkins Pipeline Job

1. Go to Jenkins Dashboard
2. Click **New Item**
3. Enter job name: `blue-reserve-pipeline`
4. Select **Pipeline**
5. Click **OK**

### Configure Pipeline:

1. **General Section**:
   - ☑ GitHub project (optional): Enter your repo URL

2. **Build Triggers** (optional):
   - ☑ GitHub hook trigger for GITScm polling (for automatic builds)
   - ☑ Poll SCM: `H/5 * * * *` (check every 5 minutes)

3. **Pipeline Section**:
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: Your Git repository URL
   - **Credentials**: Add Git credentials if private repo
   - **Branch Specifier**: `*/main` (or your branch name)
   - **Script Path**: `Jenkinsfile`

4. Click **Save**

## Step 5: Verify Jenkins Agent Setup

SSH into your Jenkins agent and verify:

```bash
# Check Podman installation
podman --version

# Check podman-compose installation
podman-compose --version

# Check if ports are available
sudo netstat -tuln | grep -E ':(8000|8080)'

# Test Podman permissions
podman ps
```

If podman-compose is not installed:
```bash
pip3 install podman-compose
```

## Step 6: Run Your First Build

1. Go to your pipeline job
2. Click **Build Now**
3. Watch the console output

### Pipeline Stages:

1. ✅ **Checkout** - Clones your repository
2. ✅ **Build Backend** - Builds backend Docker image
3. ✅ **Build Frontend** - Builds frontend Docker image
4. ✅ **Push Images** - Pushes images to registry
5. ✅ **Deploy** - Deploys containers using podman-compose
6. ✅ **Health Check** - Verifies services are running

## Troubleshooting

### Deploy Stage Fails Silently

**Cause**: Missing or incorrectly named credentials

**Solution**:
1. Verify all 12 credentials exist in Jenkins
2. Check credential IDs match exactly (case-sensitive)
3. Ensure credentials contain actual values, not placeholders

### Health Check Fails

**Symptoms**: `curl: (7) Failed to connect to localhost`

**Solutions**:
```bash
# Check if containers are running
podman ps

# Check container logs
podman logs blu-reserve-backend
podman logs blu-reserve-frontend

# Check if ports are in use
sudo netstat -tuln | grep -E ':(8000|8080)'

# Manually test endpoints
curl http://localhost:8000/seats
curl http://localhost:8080/
```

### Build Stage Fails

**Common issues**:
- Missing dependencies in requirements.txt or package.json
- Dockerfile syntax errors
- Network connectivity issues

**Solution**: Check the console output for specific error messages

### Push Stage Fails

**Symptoms**: `unauthorized: authentication required`

**Solutions**:
1. Verify registry-credentials are correct
2. Test login manually:
   ```bash
   echo "YOUR_PASSWORD" | podman login docker.io -u YOUR_USERNAME --password-stdin
   ```
3. Check if registry URL is correct (docker.io, quay.io, etc.)

### MongoDB Connection Issues

**Symptoms**: Backend container crashes or health check fails

**Solutions**:
1. Verify `mongo-url` credential is correct
2. Check MongoDB Atlas network access (whitelist Jenkins server IP)
3. Test connection manually:
   ```bash
   podman exec blu-reserve-backend python -c "from motor.motor_asyncio import AsyncIOMotorClient; client = AsyncIOMotorClient('YOUR_MONGO_URL'); print('Connected')"
   ```

## Security Best Practices

1. ✅ Never commit `.env` files (already in .gitignore)
2. ✅ Use Jenkins credentials for all secrets
3. ✅ Rotate credentials regularly
4. ✅ Use strong session secrets (min 32 characters)
5. ✅ Enable HTTPS in production
6. ✅ Restrict Jenkins access with authentication
7. ✅ Use separate credentials for dev/staging/production

## Post-Deployment Verification

After successful deployment, verify:

```bash
# Check running containers
podman ps

# Test backend API
curl http://localhost:8000/seats

# Test frontend
curl http://localhost:8080/

# Check logs
podman logs blu-reserve-backend
podman logs blu-reserve-frontend

# Test OAuth login flow
# Open browser: http://YOUR_SERVER:8080
```

## Next Steps

1. Set up monitoring and alerting
2. Configure backup strategy for MongoDB
3. Implement blue-green deployment
4. Add automated testing stages
5. Set up production environment with HTTPS

## Support

For issues or questions:
- Check Jenkins console output for detailed errors
- Review container logs: `podman logs <container-name>`
- Verify all credentials are configured correctly
- Ensure Jenkins agent has proper permissions

---

**Last Updated**: 2026-02-03
**Version**: 1.0