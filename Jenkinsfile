pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
                sh '../vibuild.sh'
            }
        }
    }
}
