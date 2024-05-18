pipeline {
    agent {
        node {
            label 'docker-flask-app'
        }
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout the code from your Git repository
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    def customImage = docker.build("docker-flask-app")
                }
            }
        }
        stage('Run Docker Container') {
            steps {
                script {
                    // Run the Docker container
                    docker.image("docker-flask-app").inside('-p 5000:5000') {
                        sh 'gunicorn --bind 0.0.0.0:5000 app:app'
                    }
                }
            }
        }
    }
}
