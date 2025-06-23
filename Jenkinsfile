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
                withCredentials([
                    string(credentialsId: 'michaelzada_kKTcgR', variable: 'BROWSERSTACK_USERNAME'),
                    string(credentialsId: 'voDkvRqyaPzkku9ncwt8', variable: 'BROWSERSTACK_ACCESS_KEY')
                ]) {
                    sh '''
                        # Activate virtual environment and run tests
                        source selenium_env/bin/activate
                        
                        # Export BrowserStack credentials
                        export BROWSERSTACK_USERNAME=$BROWSERSTACK_USERNAME
                        export BROWSERSTACK_ACCESS_KEY=$BROWSERSTACK_ACCESS_KEY
                        
                        # Run the tests
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

