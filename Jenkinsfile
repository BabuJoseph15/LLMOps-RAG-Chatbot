pipeline {

    agent any

    environment {

        BACKEND_IMAGE = "babujoseph5757/rag-chatbot"
        FRONTEND_IMAGE = "babujoseph5757/rag-chatbot-frontend"

        IMAGE_TAG = "${BUILD_NUMBER}"

        KUBECONFIG = "/var/lib/jenkins/.kube/config"

        TRIVY_TEMP_DIR = "/var/lib/jenkins/trivy-temp"

        EMAIL_RECIPIENT = "babu.joseph5757@gmail.com"
    }

    stages {

        stage('Checkout Source') {

            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {

            steps {

                withSonarQubeEnv('sonarqube-server') {

                    withCredentials([
                        string(
                            credentialsId: 'rag-sonar-token',
                            variable: 'SONAR_TOKEN'
                        )
                    ]) {

                        sh '''
                        sonar-scanner \
                        -Dsonar.projectKey=rag-chatbot \
                        -Dsonar.projectName="LLMOps RAG Chatbot" \
                        -Dsonar.host.url=$SONAR_HOST_URL \
                        -Dsonar.token=$SONAR_TOKEN
                        '''
                    }
                }
            }
        }

        stage('Quality Gate') {

            steps {

                timeout(
                    time: 10,
                    unit: 'MINUTES'
                ) {

                    waitForQualityGate abortPipeline: false
                }
            }
        }

        stage('Build Backend Image') {

            steps {

                sh '''
                docker build \
                -f backend/Dockerfile \
                -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
                .
                '''
            }
        }

        stage('Build Frontend Image') {

            steps {

                sh '''
                docker build \
                -f frontend/Dockerfile \
                -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                .
                '''
            }
        }

        stage('Trivy Scan Backend') {

            steps {

                sh '''
                mkdir -p ${TRIVY_TEMP_DIR}

                export TMPDIR=${TRIVY_TEMP_DIR}

                trivy image \
                --timeout 30m \
                --skip-version-check \
                --scanners vuln \
                --severity HIGH,CRITICAL \
                --exit-code 0 \
                ${BACKEND_IMAGE}:${IMAGE_TAG}
                '''
            }
        }

        stage('Trivy Scan Frontend') {

            steps {

                sh '''
                trivy image \
                --timeout 15m \
                --skip-version-check \
                --scanners vuln \
                --severity HIGH,CRITICAL \
                --exit-code 0 \
                ${FRONTEND_IMAGE}:${IMAGE_TAG}
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

                docker tag ${BACKEND_IMAGE}:${IMAGE_TAG} \
                ${BACKEND_IMAGE}:latest

                docker push ${BACKEND_IMAGE}:latest
                '''
            }
        }

        stage('Push Frontend Image') {

            steps {

                sh '''
                docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}

                docker tag ${FRONTEND_IMAGE}:${IMAGE_TAG} \
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
    }

    post {

        success {

            emailext(
                to: "${EMAIL_RECIPIENT}",
                subject: "SUCCESS - ${JOB_NAME} #${BUILD_NUMBER}",
                body: """
RAG Chatbot Deployment Successful

Build Number: ${BUILD_NUMBER}

Backend:
${BACKEND_IMAGE}:${IMAGE_TAG}

Frontend:
${FRONTEND_IMAGE}:${IMAGE_TAG}

Build URL:
${BUILD_URL}
"""
            )
        }

        failure {

            emailext(
                to: "${EMAIL_RECIPIENT}",
                subject: "FAILED - ${JOB_NAME} #${BUILD_NUMBER}",
                body: """
RAG Chatbot Deployment Failed

Build URL:
${BUILD_URL}
"""
            )
        }

        always {

            sh '''
            docker builder prune -f || true

            docker image prune -f || true

            docker container prune -f || true
            '''

            cleanWs()
        }
    }
}
