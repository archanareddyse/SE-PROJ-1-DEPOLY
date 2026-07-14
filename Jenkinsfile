pipeline {
    agent any

    environment {
        BACKEND_IMAGE = "archanareddycse/stage1-backend:latest"
        FRONTEND_IMAGE = "archanareddycse/stage1-frontend:latest"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Backend') {
            steps {
                dir('backend') {
                    bat 'docker build -t %BACKEND_IMAGE% .'
                }
            }
        }

        stage('Build Frontend') {
            steps {
                dir('frontend') {
                    bat 'docker build -t %FRONTEND_IMAGE% .'
                }
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat 'echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'
                }
            }
        }

        stage('Push Backend Image') {
            steps {
                bat 'docker push %BACKEND_IMAGE%'
            }
        }

        stage('Push Frontend Image') {
            steps {
                bat 'docker push %FRONTEND_IMAGE%'
            }
        }
    }
}
