 pipeline {
    agent any
    
    environment {
        BROWSERSTACK_USERNAME = credentials('browserstack-username')
        BROWSERSTACK_ACCESS_KEY = credentials('browserstack-access-key')
    }
    
    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                git 'https://github.com/leroylannister/selenium-browserstack-demo'
            }
        }
        
        stage('Set up Python Environment') {
            steps {
                sh '''
                    python3 -m venv selenium_env
                    source selenium_env/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Enhanced Selenium Tests') {
            steps {
                browserstack {
                    steps {
                        sh '''
                            source selenium_env/bin/activate
                            python corrected-test.py
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up workspace...'
            deleteDir()
        }
        success {
            echo 'Enhanced tests completed successfully!'
        }
        failure {
            echo 'Enhanced tests failed - check logs for details'
        }
    }
}
