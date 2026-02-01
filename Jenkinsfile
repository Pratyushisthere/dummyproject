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
                sh """
                    cd ${WORKSPACE}
                    podman-compose down || true
                    podman-compose up -d
                    sleep 10
                    echo "✅ Deployment complete"
                """
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
