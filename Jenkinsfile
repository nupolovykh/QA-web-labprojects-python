    pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/nupolovykh/QA-web-labprojects-python.git'
            }
        }
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r lab11/requirements.txt'
                sh 'pip install -r lab12/requirements.txt'
            }
        }
        stage('Run Tests Lab11') {
            steps {
                sh 'pytest "lab11/tests.py" -v'
                sh 'pytest "lab11/tests.py" --junitxml="lab11/report.xml"'
                archiveArtifacts artifacts: 'lab11/report.xml', allowEmptyArchive: true
            }
        }
        stage('Run Tests Lab12') {
            steps {
                sh 'pytest "lab12/api_tests.py" -v'
                sh 'pytest "lab12/api_tests.py" --junitxml="lab12/report.xml"'
                archiveArtifacts artifacts: 'lab12/report.xml', allowEmptyArchive: true
            }
        }
    }
}
