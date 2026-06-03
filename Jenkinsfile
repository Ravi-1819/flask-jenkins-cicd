pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Ravi-1819/flask-jenkins-cicd.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t flask-app .'
            }
        }

        stage('Stop Old Container') {
            steps {
                sh 'docker stop flask-app || true'
                sh 'docker rm flask-app || true'
            }
        }

        stage('Run New Container') {
            steps {
                sh 'docker run -d -p 5000:5000 --name flask-app flask-app'
            }
        }
    }

    post {
        success {
            echo "🚀 Deployment Successful!"
        }
        failure {
            echo "❌ Build Failed!"
        }
    }
}
