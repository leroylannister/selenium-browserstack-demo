pipeline {
    agent any
    environment {
        BROWSERSTACK_USERNAME = credentials('michaelzada_kKTcgR')
        BROWSERSTACK_ACCESS_KEY = credentials('voDkvRqyaPzkku9ncwt8ID')
    }
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/leroylannister/selenium-browserstack-demo.git'
            }
        }
        stage('Set up Python') {
            steps {
                sh '''
                python3 -m venv selenium_env
                source selenium_env/bin/activate
                pip install -r requirements.txt
                '''
            }
        }
        stage('Run Selenium Tests') {
            steps {
                sh '''
                source selenium_env/bin/activate
                python tests/test_bstackdemo.py
                '''
            }
        }
    }
}
