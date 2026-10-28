pipeline {

    agent any

    environment {
        DOCKER_IMAGE = "babujoseph5757/rag-chatbot"
    }

    options {
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'master',
                url: 'https://github.com/YOUR_GITHUB_USERNAME/LLMOps-RAG-Chatbot.git'
            }
        }

        stage('Create Virtual Environment') {
            steps {
                sh '''
                python3 -m venv venv

                . venv/bin/activate

                python --version

                pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                . venv/bin/activate

                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                . venv/bin/activate

                pytest
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build \
                -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .

                docker tag \
                ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Push Docker Image') {

            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {

                    sh '''
                    echo "$DOCKER_PASS" | docker login \
                    -u "$DOCKER_USER" \
                    --password-stdin

                    docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}

                    docker push ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }
    }

    post {

        success {
            echo '✅ RAG Chatbot pipeline successful'
        }

        failure {
            echo '❌ Pipeline failed'
        }

        always {
            cleanWs()
        }
    }
}
