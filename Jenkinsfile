pipeline {
    // Run this pipeline on any available Jenkins agent
    agent any
    
    stages {
        // Stage 1: Checkout source code from Git repository
        stage('Checkout') {
            steps {
                // Clone the main branch of the Selenium BrowserStack demo repository
                git branch: 'main', url: 'https://github.com/leroylannister/selenium-browserstack-demo.git'
            }
        }
        
        // Stage 2: Set up Python environment and install dependencies
        stage('Set up Python') {
            steps {
                sh '''
                # Create a Python virtual environment named 'selenium_env'
                python3 -m venv selenium_env
                
                # Activate the virtual environment
                source selenium_env/bin/activate
                
                # Install required Python packages from requirements.txt
                pip install -r requirements.txt
                '''
            }
        }
        
        // Stage 3: Execute Selenium tests using BrowserStack
        stage('Run Selenium Tests') {
            steps {
                // Use BrowserStack credentials stored in Jenkins for authentication
                browserstack(credentialsId: 'd165da47-3c30-4ac2-9ab8-0bd037b78e0e') {
                    sh '''
                    # Activate the Python virtual environment
                    source selenium_env/bin/activate
                    
                    # Run the Selenium test suite for BrowserStack demo
                    python tests/test_bstackdemo.py
                    '''
                }
            }
        }
    }
}

