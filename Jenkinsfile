pipeline {

    agent any

    environment {

        DOCKER_IMAGE = "babujoseph5757/rag-chatbot"
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

        stage('Verify Workspace') {

            steps {

                sh '''
                pwd
                ls -ltr
                '''
            }
        }

        stage('Install Dependencies') {

            steps {

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

        stage('Verify Pytest') {

            steps {

                sh '''
                python3 -m pip show pytest || true
                '''
            }
        }

        stage('Run Unit Tests') {

            steps {

                sh '''
                if [ -d tests ]; then
                    python3 -m pytest tests/
                else
                    echo "No tests directory found. Skipping..."
                fi
                '''
            }
        }

        stage('Build Docker Image') {

            steps {

                sh '''
                docker build \
                -t ${DOCKER_IMAGE}:${IMAGE_TAG} .
                '''
            }
        }

        stage('Trivy Security Scan') {

            steps {

                sh '''
                mkdir -p ${TRIVY_TEMP_DIR}

                export TMPDIR=${TRIVY_TEMP_DIR}

                trivy image \
                --skip-version-check \
                --severity HIGH,CRITICAL \
                --exit-code 0 \
                ${DOCKER_IMAGE}:${IMAGE_TAG}
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

        stage('Push Docker Image') {

            steps {

                sh '''
                docker push ${DOCKER_IMAGE}:${IMAGE_TAG}

                docker tag \
                ${DOCKER_IMAGE}:${IMAGE_TAG} \
                ${DOCKER_IMAGE}:latest

                docker push ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Deploy To Kubernetes') {

            steps {

                sh '''
                kubectl set image deployment/rag-chatbot \
                rag-chatbot=${DOCKER_IMAGE}:${IMAGE_TAG}

                kubectl rollout status deployment/rag-chatbot \
                --timeout=300s
                '''
            }
        }

        stage('Verify Deployment') {

            steps {

                sh '''
                echo "===== Pods ====="
                kubectl get pods

                echo "===== Deployments ====="
                kubectl get deployment

                echo "===== Services ====="
                kubectl get svc
                '''
            }
        }
    }

    post {

        success {

            echo '✅ RAG Chatbot deployment successful'
        }

        failure {

            echo '❌ Pipeline failed'
        }

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
    }
}
