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
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Run Tests') {
            steps {
				sh 'pytest -v'
                sh 'pytest --junitxml=report.xml'
                archiveArtifacts artifacts: 'report.xml', allowEmptyArchive: true
            }
        }
    }
}