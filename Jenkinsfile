pipeline {

    agent any

    environment {

        BACKEND_IMAGE = "babujoseph5757/rag-chatbot"
        FRONTEND_IMAGE = "babujoseph5757/rag-chatbot-frontend"

        IMAGE_TAG = "${BUILD_NUMBER}"

        KUBECONFIG = "/var/lib/jenkins/.kube/config"

        TRIVY_TEMP_DIR = "/var/lib/jenkins/trivy-temp"

        PATH = "/var/lib/jenkins/.local/bin:${env.PATH}"
    }

    options {

        timestamps()

        buildDiscarder(
            logRotator(
                numToKeepStr: '10'
            )
        )
    }

    stages {

        stage('Checkout Source') {

            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {

            steps {

                dir('backend') {

                    sh '''
                    python3 --version

                    python3 -m pip install --upgrade pip

                    python3 -m pip install \
                    --user \
                    --no-cache-dir \
                    -r requirements.txt
                    '''
                }
            }
        }

        stage('Run Unit Tests') {

            steps {

                sh '''
                python3 -m pytest tests/ -v
                '''
            }
        }

        stage('Build Backend Image') {

            steps {

                sh '''
                docker build \
                -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
                ./backend
                '''
            }
        }

        stage('Build Frontend Image') {

            steps {

                sh '''
                docker build \
                -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                ./frontend
                '''
            }
        }

        stage('Trivy Scan Backend') {

            steps {

                sh '''
                mkdir -p ${TRIVY_TEMP_DIR}

                export TMPDIR=${TRIVY_TEMP_DIR}

                trivy image \
                --skip-version-check \
                --severity HIGH,CRITICAL \
                --exit-code 0 \
                ${BACKEND_IMAGE}:${IMAGE_TAG}
                '''
            }
        }

        stage('Docker Login') {

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
                    '''
                }
            }
        }

        stage('Push Backend Image') {

            steps {

                sh '''
                docker push ${BACKEND_IMAGE}:${IMAGE_TAG}

                docker tag \
                ${BACKEND_IMAGE}:${IMAGE_TAG} \
                ${BACKEND_IMAGE}:latest

                docker push ${BACKEND_IMAGE}:latest
                '''
            }
        }

        stage('Push Frontend Image') {

            steps {

                sh '''
                docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}

                docker tag \
                ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                ${FRONTEND_IMAGE}:latest

                docker push ${FRONTEND_IMAGE}:latest
                '''
            }
        }

        stage('Deploy Backend') {

            steps {

                sh '''
                kubectl set image deployment/rag-chatbot \
                rag-chatbot=${BACKEND_IMAGE}:${IMAGE_TAG}

                kubectl rollout status deployment/rag-chatbot \
                --timeout=300s
                '''
            }
        }

        stage('Deploy Frontend') {

            steps {

                sh '''
                kubectl set image deployment/rag-chatbot-frontend \
                rag-chatbot-frontend=${FRONTEND_IMAGE}:${IMAGE_TAG}

                kubectl rollout status deployment/rag-chatbot-frontend \
                --timeout=300s
                '''
            }
        }

        stage('Verify Deployment') {

            steps {

                sh '''
                kubectl get deployment

                kubectl get pods

                kubectl get svc
                '''
            }
        }
    }

    post {

        always {

            sh '''
            rm -rf ~/.cache/pip || true

            rm -rf ${TRIVY_TEMP_DIR}/* || true

            docker container prune -f || true

            docker image prune -f || true

            docker builder prune -f || true
            '''

            cleanWs()
        }

        success {

            echo "✅ Backend + Frontend deployment successful"
        }

        failure {

            echo "❌ Pipeline failed"
        }
    }
}
