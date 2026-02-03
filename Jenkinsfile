pipeline {
    agent any
    
    environment {
        REGISTRY_URL = credentials('container-registry-url')
        REGISTRY_CREDENTIALS = credentials('registry-credentials')
        REGISTRY_NAMESPACE = 'officialdarsh'  // CHANGE THIS!
        
        BACKEND_IMAGE = "${REGISTRY_URL}/${REGISTRY_NAMESPACE}/blu-reserve-backend"
        FRONTEND_IMAGE = "${REGISTRY_URL}/${REGISTRY_NAMESPACE}/blu-reserve-frontend"
        
        BUILD_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "🔄 Checking out code..."
                checkout scm
            }
        }
        
        stage('Build Backend') {
            steps {
                echo "🐳 Building Backend..."
                dir('backend') {
                    sh """
                        podman build -t ${BACKEND_IMAGE}:${BUILD_TAG} -t ${BACKEND_IMAGE}:latest .
                        echo "✅ Backend built successfully"
                    """
                }
            }
        }
        
        stage('Build Frontend') {
            steps {
                echo "🐳 Building Frontend..."
                dir('frontend') {
                    sh """
                        podman build -t ${FRONTEND_IMAGE}:${BUILD_TAG} -t ${FRONTEND_IMAGE}:latest .
                        echo "✅ Frontend built successfully"
                    """
                }
            }
        }
        
        stage('Push Images') {
            steps {
                echo "📤 Pushing to registry..."
                sh """
                    echo ${REGISTRY_CREDENTIALS_PSW} | podman login ${REGISTRY_URL} -u ${REGISTRY_CREDENTIALS_USR} --password-stdin
                    podman push ${BACKEND_IMAGE}:${BUILD_TAG}
                    podman push ${BACKEND_IMAGE}:latest
                    podman push ${FRONTEND_IMAGE}:${BUILD_TAG}
                    podman push ${FRONTEND_IMAGE}:latest
                    podman logout ${REGISTRY_URL}
                    echo "✅ Images pushed successfully"
                """
            }
        }
        
        stage('Deploy') {
            steps {
                echo "🚀 Deploying containers..."
                withCredentials([
                    string(credentialsId: 'mongo-url', variable: 'MONGO_URL'),
                    string(credentialsId: 'session-secret', variable: 'SESSION_SECRET'),
                    string(credentialsId: 'client-id', variable: 'CLIENT_ID'),
                    string(credentialsId: 'client-secret', variable: 'CLIENT_SECRET'),
                    string(credentialsId: 'token-url', variable: 'TOKEN_URL'),
                    string(credentialsId: 'auth-endpoint', variable: 'AUTH_ENDPOINT'),
                    string(credentialsId: 'jwks-url', variable: 'JWKS_URL'),
                    string(credentialsId: 'jwt-issuer', variable: 'JWT_ISSUER'),
                    string(credentialsId: 'redirect-uri', variable: 'REDIRECT_URI'),
                    string(credentialsId: 'frontend-url', variable: 'FRONTEND_URL')
                ]) {
                    sh """
                        cd ${WORKSPACE}
                        
                        # Create .env file from Jenkins credentials
                        cat > .env << EOF
MONGO_URL=\${MONGO_URL}
SESSION_SECRET=\${SESSION_SECRET}
CLIENT_ID=\${CLIENT_ID}
CLIENT_SECRET=\${CLIENT_SECRET}
TOKEN_URL=\${TOKEN_URL}
AUTH_ENDPOINT=\${AUTH_ENDPOINT}
JWKS_URL=\${JWKS_URL}
JWT_ISSUER=\${JWT_ISSUER}
REDIRECT_URI=\${REDIRECT_URI}
FRONTEND_URL=\${FRONTEND_URL}
PYTHONUNBUFFERED=1
BACKEND_PORT=8000
FRONTEND_PORT=8080
VITE_API_URL=http://127.0.0.1:8000
EOF
                        
                        podman-compose down || true
                        
                        # Remove old images to force fresh pull
                        podman rmi blu-reserve-backend:latest || true
                        podman rmi blu-reserve-frontend:latest || true
                        
                        # Rebuild without cache
                        podman-compose build --no-cache
                        podman-compose up -d
                        
                        sleep 10
                        echo "✅ Deployment complete"
                    """
                }
            }
        }

        
        stage('Health Check') {
            steps {
                echo "🏥 Running health checks..."
                sh """
                    curl -f http://localhost:8000/seats || exit 1
                    curl -f http://localhost:8080/ || exit 1
                    echo "✅ All health checks passed"
                """
            }
        }
    }
    
    post {
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}
