pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 -m unittest discover -s tests -v'
                    } else {
                        bat 'python -m unittest discover -s tests -v'
                    }
                }
            }
        }

        stage('Smoke') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 -m clawbot "hello harness"'
                    } else {
                        bat 'python -m clawbot "hello harness"'
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'mkdir -p dist && git archive --format=zip --output=dist/clawbot-harness.zip HEAD'
                    } else {
                        bat 'if not exist dist mkdir dist && git archive --format=zip --output=dist/clawbot-harness.zip HEAD'
                    }
                }
            }
        }

        stage('Deliver') {
            steps {
                archiveArtifacts(
                    artifacts: 'dist/clawbot-harness.zip',
                    fingerprint: true
                )
            }
        }
    }
}
