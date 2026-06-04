pipeline {
    agent any

    environment {
        DOCKER_HUB_REPO = 'your-dockerhub-username/blood-bank'
        IMAGE_TAG = "${BUILD_NUMBER}"
        CONTAINER_NAME = 'blood-bank-app'
        EC2_PORT = '5000'
    }

    stages {

        stage('Checkout') {
            steps {
                echo '🩸 Blood Bank - Code checkout...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh """
                    docker build -t ${DOCKER_HUB_REPO}:${IMAGE_TAG} \
                                 -t ${DOCKER_HUB_REPO}:latest \
                                 ./blood-bank
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo '📤 Pushing to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}
                        docker push ${DOCKER_HUB_REPO}:latest
                    """
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo '🚀 Deploying to EC2...'
                sh """
                    docker pull ${DOCKER_HUB_REPO}:latest

                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true

                    docker volume create blood_data || true

                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --restart unless-stopped \
                        -p ${EC2_PORT}:5000 \
                        -v blood_data:/data \
                        -e DB_PATH=/data/blood_bank.db \
                        ${DOCKER_HUB_REPO}:latest
                """
            }
        }

        stage('Health Check') {
            steps {
                echo '✅ Health check...'
                sh """
                    sleep 5
                    curl -f http://localhost:${EC2_PORT}/api/stats || exit 1
                    echo "✅ Blood Bank app is LIVE!"
                """
            }
        }
    }

    post {
        success {
            echo """
            ╔══════════════════════════════════════╗
            ║  🩸 BLOOD BANK DEPLOYED SUCCESSFULLY ║
            ║  URL: http://YOUR_EC2_IP:5000        ║
            ╚══════════════════════════════════════╝
            """
        }
        failure {
            echo '❌ Deployment failed! Check logs above.'
        }
        always {
            sh 'docker logout || true'
        }
    }
}
    }
}
