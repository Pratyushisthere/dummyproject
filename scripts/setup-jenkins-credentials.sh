#!/bin/bash

# Jenkins Credentials Setup Helper Script
# This script helps you configure all required Jenkins credentials

set -e

echo "=================================================="
echo "  Jenkins Credentials Setup Helper"
echo "  Blue Reserve Project"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create a .env file with your configuration first."
    exit 1
fi

echo -e "${GREEN}✓ Found .env file${NC}"
echo ""

# Load .env file
export $(cat .env | grep -v '^#' | xargs)

echo "=================================================="
echo "  STEP 1: Verify Your Configuration"
echo "=================================================="
echo ""

echo "The following values will be used for Jenkins credentials:"
echo ""
echo "1.  MONGO_URL: ${MONGO_URL:0:30}..."
echo "2.  SESSION_SECRET: ${SESSION_SECRET:0:20}..."
echo "3.  CLIENT_ID: ${CLIENT_ID:0:20}..."
echo "4.  CLIENT_SECRET: ${CLIENT_SECRET:0:20}..."
echo "5.  TOKEN_URL: $TOKEN_URL"
echo "6.  AUTH_ENDPOINT: $AUTH_ENDPOINT"
echo "7.  JWKS_URL: $JWKS_URL"
echo "8.  JWT_ISSUER: $JWT_ISSUER"
echo "9.  REDIRECT_URI: $REDIRECT_URI"
echo "10. FRONTEND_URL: $FRONTEND_URL"
echo ""

read -p "Do these values look correct? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Please update your .env file and run this script again.${NC}"
    exit 1
fi

echo ""
echo "=================================================="
echo "  STEP 2: Container Registry Configuration"
echo "=================================================="
echo ""

read -p "Enter your container registry URL (e.g., docker.io, quay.io): " REGISTRY_URL
read -p "Enter your registry username: " REGISTRY_USERNAME
read -sp "Enter your registry password/token: " REGISTRY_PASSWORD
echo ""

echo ""
echo "=================================================="
echo "  STEP 3: Jenkins Credentials Summary"
echo "=================================================="
echo ""

cat > jenkins-credentials-config.txt << EOF
=== JENKINS CREDENTIALS CONFIGURATION ===
Generated: $(date)

Copy these credentials into Jenkins:
Go to: Jenkins → Manage Jenkins → Credentials → System → Global credentials → Add Credentials

For each credential:
1. Click "Add Credentials"
2. Kind: Secret text (or Username with password for #12)
3. Scope: Global
4. Secret: [paste value below]
5. ID: [use exact ID below]
6. Click "Create"

=== APPLICATION CREDENTIALS ===

1. ID: mongo-url
   Kind: Secret text
   Secret: $MONGO_URL

2. ID: session-secret
   Kind: Secret text
   Secret: $SESSION_SECRET

3. ID: client-id
   Kind: Secret text
   Secret: $CLIENT_ID

4. ID: client-secret
   Kind: Secret text
   Secret: $CLIENT_SECRET

5. ID: token-url
   Kind: Secret text
   Secret: $TOKEN_URL

6. ID: auth-endpoint
   Kind: Secret text
   Secret: $AUTH_ENDPOINT

7. ID: jwks-url
   Kind: Secret text
   Secret: $JWKS_URL

8. ID: jwt-issuer
   Kind: Secret text
   Secret: $JWT_ISSUER

9. ID: redirect-uri
   Kind: Secret text
   Secret: $REDIRECT_URI

10. ID: frontend-url
    Kind: Secret text
    Secret: $FRONTEND_URL

=== CONTAINER REGISTRY CREDENTIALS ===

11. ID: container-registry-url
    Kind: Secret text
    Secret: $REGISTRY_URL

12. ID: registry-credentials
    Kind: Username with password
    Username: $REGISTRY_USERNAME
    Password: $REGISTRY_PASSWORD

=== NEXT STEPS ===

1. Open Jenkins in your browser
2. Navigate to: Manage Jenkins → Credentials → System → Global credentials
3. Add each credential above using the exact ID specified
4. Update Jenkinsfile line 7: REGISTRY_NAMESPACE = '$REGISTRY_USERNAME'
5. Commit and push your changes
6. Run the Jenkins pipeline

=== VERIFICATION CHECKLIST ===

□ All 12 credentials added to Jenkins
□ Credential IDs match exactly (case-sensitive)
□ REGISTRY_NAMESPACE updated in Jenkinsfile
□ podman-compose installed on Jenkins agent
□ Jenkins agent has network access to MongoDB Atlas
□ Ports 8000 and 8080 available on Jenkins agent

EOF

echo -e "${GREEN}✓ Configuration file created: jenkins-credentials-config.txt${NC}"
echo ""
echo "=================================================="
echo "  IMPORTANT: Security Notice"
echo "=================================================="
echo ""
echo -e "${RED}⚠️  The file 'jenkins-credentials-config.txt' contains sensitive information!${NC}"
echo ""
echo "Actions to take:"
echo "1. Use this file to configure Jenkins credentials"
echo "2. DELETE this file after configuration: rm jenkins-credentials-config.txt"
echo "3. Never commit this file to version control"
echo ""

# Add to gitignore if not already there
if ! grep -q "jenkins-credentials-config.txt" .gitignore 2>/dev/null; then
    echo "jenkins-credentials-config.txt" >> .gitignore
    echo -e "${GREEN}✓ Added jenkins-credentials-config.txt to .gitignore${NC}"
fi

echo ""
echo "=================================================="
echo "  Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Open jenkins-credentials-config.txt"
echo "2. Follow the instructions to add credentials to Jenkins"
echo "3. Update REGISTRY_NAMESPACE in Jenkinsfile"
echo "4. Delete jenkins-credentials-config.txt when done"
echo "5. Run your Jenkins pipeline"
echo ""
echo -e "${GREEN}Good luck with your deployment! 🚀${NC}"

# Made with Bob
