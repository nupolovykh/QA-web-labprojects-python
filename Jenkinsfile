    pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/DonutsEmperor/Python-parsing-with-selenium.git'
            }
        }
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r lab=11/requirements.txt'
                sh 'pip install -r lab=12/requirements.txt'
            }
        }
        stage('Run Tests Lab11') {
            steps {
                sh 'pytest "lab=11/tests.py" -v'
                sh 'pytest "lab=11/tests.py" --junitxml="lab=11/report.xml"'
                archiveArtifacts artifacts: 'lab=11/report.xml', allowEmptyArchive: true
            }
        }
        stage('Run Tests Lab12') {
            steps {
                sh 'uvicorn "lab=12.main:app" --host 0.0.0.0 --port 8000 &'
                sh 'sleep 5'
                sh 'pytest "lab=12/api_tests.py" -v'
                sh 'pytest "lab=12/api_tests.py" --junitxml="lab=12/report.xml"'
                archiveArtifacts artifacts: 'lab=12/report.xml', allowEmptyArchive: true
            }
        }
    }
}