pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                // Clean workspace before checkout
                deleteDir()
                
                // Checkout code from repository
                git branch: 'main', 
                    url: 'https://github.com/leroylannister/selenium-browserstack-demo.git'
            }
        }
        
        stage('Set up Python') {
            steps {
                sh '''
                    # Create virtual environment
                    python3 -m venv selenium_env
                    
                    # Activate virtual environment and install dependencies
                    source selenium_env/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                // Use the BrowserStack plugin wrapper
                browserstack(credentialsId: 'd165da47-3c30-4ac2-9ab8-0bd037b78e0e') {
                    sh '''
                        # Activate virtual environment and run tests
                        source selenium_env/bin/activate
                        
                        # BrowserStack plugin sets these environment variables automatically
                        python tests/test_bstackdemo.py
                    '''
                }
            }
        }
    }
    
    post {
        always {
            // Clean up workspace
            echo 'Cleaning up workspace...'
            deleteDir()
        }
        success {
            echo 'Tests completed successfully!'
        }
        failure {
            echo 'Tests failed! Check the logs for details.'
        }
    }
}