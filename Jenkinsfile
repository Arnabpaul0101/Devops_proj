pipeline {
    agent any

    environment {
        IMAGE_NAME = 'bloodbank-app'
        IMAGE_TAG  = "${BUILD_NUMBER}"
        REGISTRY   = 'your-dockerhub-username'   // TODO: replace with your Docker Hub username
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "Source checked out from branch: ${env.BRANCH_NAME}"
            }
        }

        stage('Build') {
            steps {
                dir('app') {
                    sh "docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ."
                    sh "docker tag ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest"
                }
                echo "Image built: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        stage('Test') {
            steps {
                sh """
                    docker run --rm \
                        -e FLASK_ENV=testing \
                        -v \$(pwd)/tests:/app/tests \
                        ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
                        python -m pytest tests/ -v --tb=short
                """
            }
        }

        stage('Push Image') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker push ${REGISTRY}/${IMAGE_NAME}:latest"
                }
                echo "Image pushed: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'docker-compose down --remove-orphans || true'
                sh "IMAGE_TAG=${IMAGE_TAG} REGISTRY=${REGISTRY} docker-compose up -d"
                sh 'docker-compose ps'
                echo "Application deployed on port 5000"
            }
        }

    }

    post {
        always {
            sh 'docker logout || true'
        }
        success {
            echo "Pipeline succeeded for build #${BUILD_NUMBER}"
        }
        failure {
            echo "Pipeline FAILED for build #${BUILD_NUMBER}. Check logs above."
        }
    }
}
