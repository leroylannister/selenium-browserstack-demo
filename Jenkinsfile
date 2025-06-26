pipeline {
    agent any
    
    // Global environment variables and configuration
    environment {
        // BrowserStack credentials - using Jenkins credential store
        BROWSERSTACK_USERNAME = credentials('browserstack-username')
        BROWSERSTACK_ACCESS_KEY = credentials('browserstack-access-key')
        
        // Python environment configuration
        PYTHON_VERSION = '3.13'
        VENV_NAME = 'selenium_test_env'
        
        // Repository and test configuration
        GIT_REPO_URL = 'https://github.com/leroylannister/selenium-browserstack-demo'
        TEST_SCRIPT = 'test_bstackdemo.py'
        
        // Pipeline metadata
        BUILD_TIMESTAMP = sh(script: 'date +%Y%m%d_%H%M%S', returnStdout: true).trim()
    }
    
    // Pipeline options for better control
    options {
        // Keep only last 10 builds to save disk space
        buildDiscarder(logRotator(numToKeepStr: '10'))
        
        // Timeout the entire pipeline after 30 minutes
        timeout(time: 30, unit: 'MINUTES')
        
        // Skip checkout to default SCM (we'll do it manually)
        skipDefaultCheckout(true)
        
        // Add timestamps to console output
        timestamps()
    }
    
    stages {
        stage('Environment Setup') {
            steps {
                script {
                    // Log pipeline start information
                    echo "Starting Selenium BrowserStack Pipeline"
                    echo "Build ID: ${env.BUILD_ID}"
                    echo "Build Timestamp: ${env.BUILD_TIMESTAMP}"
                    echo "Node: ${env.NODE_NAME}"
                    
                    // Verify required tools are available
                    sh '''
                        echo "Verifying system requirements..."
                        python3 --version || { echo "Python3 not found"; exit 1; }
                        git --version || { echo "Git not found"; exit 1; }
                        echo "System requirements verified successfully"
                    '''
                }
            }
        }
        
        stage('Source Code Checkout') {
            steps {
                script {
                    try {
                        // Clean workspace before checkout
                        echo "Cleaning workspace..."
                        deleteDir()
                        
                        // Clone repository with better error handling
                        echo "Checking out source code from: ${env.GIT_REPO_URL}"
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: '*/main']], // Specify branch explicitly
                            doGenerateSubmoduleConfigurations: false,
                            extensions: [
                                [$class: 'CleanBeforeCheckout'],
                                [$class: 'CloneOption', depth: 1, shallow: true] // Shallow clone for faster checkout
                            ],
                            submoduleCfg: [],
                            userRemoteConfigs: [[url: env.GIT_REPO_URL]]
                        ])
                        
                        // Verify checkout was successful
                        sh '''
                            echo "Verifying checkout..."
                            ls -la
                            if [ ! -f requirements.txt ]; then
                                echo "ERROR: requirements.txt not found in repository"
                                exit 1
                            fi
                            if [ ! -f "${TEST_SCRIPT}" ]; then
                                echo "ERROR: Test script ${TEST_SCRIPT} not found in repository"
                                exit 1
                            fi
                            echo "Source code checkout verified successfully"
                        '''
                    } catch (Exception e) {
                        error "Failed to checkout source code: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Python Environment Setup') {
            steps {
                script {
                    try {
                        echo "Setting up Python virtual environment..."
                        
                        // Create and configure virtual environment with better error handling
                        sh '''
                            # Remove existing virtual environment if it exists
                            if [ -d "${VENV_NAME}" ]; then
                                echo "Removing existing virtual environment..."
                                rm -rf "${VENV_NAME}"
                            fi
                            
                            # Create new virtual environment
                            echo "Creating virtual environment: ${VENV_NAME}"
                            python3 -m venv "${VENV_NAME}"
                            
                            # Activate virtual environment and verify
                            source "${VENV_NAME}/bin/activate"
                            echo "Virtual environment activated"
                            echo "Python version: $(python --version)"
                            echo "Pip version: $(pip --version)"
                            
                            # Upgrade pip to latest version
                            echo "Upgrading pip..."
                            pip install --upgrade pip
                            
                            # Install dependencies from requirements.txt
                            echo "Installing dependencies from requirements.txt..."
                            pip install -r requirements.txt
                            
                            # Verify critical packages are installed
                            echo "Verifying critical packages..."
                            pip show selenium || { echo "Selenium not installed properly"; exit 1; }
                            
                            echo "Python environment setup completed successfully"
                        '''
                    } catch (Exception e) {
                        error "Failed to set up Python environment: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Pre-Test Validation') {
            steps {
                script {
                    echo "Performing pre-test validation..."
                    
                    // Validate BrowserStack credentials are available
                    sh '''
                        source "${VENV_NAME}/bin/activate"
                        
                        # Check if credentials are properly set
                        if [ -z "$BROWSERSTACK_USERNAME" ] || [ -z "$BROWSERSTACK_ACCESS_KEY" ]; then
                            echo "ERROR: BrowserStack credentials not properly configured"
                            exit 1
                        fi
                        
                        echo "BrowserStack credentials validated (username: ${BROWSERSTACK_USERNAME})"
                        
                        # Perform syntax check on test script
                        echo "Validating test script syntax..."
                        python -m py_compile "${TEST_SCRIPT}"
                        echo "Test script syntax validation passed"
                    '''
                }
            }
        }
        
        stage('Execute Selenium Tests') {
            steps {
                script {
                    try {
                        echo "Starting Selenium test execution on BrowserStack..."
                        
                        // Use BrowserStack plugin with proper credential handling
                        browserstack(credentialsId: '08559fdd-ecab-4f7a-a440-8975c75f02a5') {
                            // Execute tests with enhanced logging and error handling
                            sh '''
                                source "${VENV_NAME}/bin/activate"
                                
                                echo "Activated virtual environment for test execution"
                                echo "Current working directory: $(pwd)"
                                echo "Python path: $(which python)"
                                
                                # Set additional environment variables for test execution
                                export PYTHONPATH="${PYTHONPATH}:$(pwd)"
                                export SELENIUM_LOG_LEVEL="INFO"
                                
                                # Execute the test script with proper error handling
                                echo "Executing test script: ${TEST_SCRIPT}"
                                python "${TEST_SCRIPT}" 2>&1 | tee test_execution.log
                                
                                # Check if test execution was successful
                                TEST_EXIT_CODE=${PIPESTATUS[0]}
                                if [ $TEST_EXIT_CODE -ne 0 ]; then
                                    echo "ERROR: Test execution failed with exit code: $TEST_EXIT_CODE"
                                    exit $TEST_EXIT_CODE
                                fi
                                
                                echo "Test execution completed successfully"
                            '''
                        }
                    } catch (Exception e) {
                        // Enhanced error handling with detailed logging
                        echo "Test execution failed: ${e.getMessage()}"
                        
                        // Attempt to capture additional debug information
                        sh '''
                            echo "=== DEBUG INFORMATION ==="
                            echo "Workspace contents:"
                            ls -la
                            
                            echo "Virtual environment status:"
                            source "${VENV_NAME}/bin/activate" 2>/dev/null && echo "Virtual env activated successfully" || echo "Failed to activate virtual env"
                            
                            echo "Installed packages:"
                            source "${VENV_NAME}/bin/activate" && pip list 2>/dev/null || echo "Could not list packages"
                            
                            echo "Test execution log (if available):"
                            if [ -f test_execution.log ]; then
                                tail -50 test_execution.log
                            else
                                echo "No test execution log found"
                            fi
                        '''
                        
                        error "Selenium test execution failed. Check logs for details."
                    }
                }
            }
        }
        
        stage('Test Results Processing') {
            steps {
                script {
                    echo "Processing test results and artifacts..."
                    
                    // Archive test logs and any generated reports
                    sh '''
                        # Create results directory
                        mkdir -p test_results
                        
                        # Archive test execution log if it exists
                        if [ -f test_execution.log ]; then
                            cp test_execution.log test_results/
                            echo "Test execution log archived"
                        fi
                        
                        # Look for any test reports or screenshots
                        find . -name "*.png" -o -name "*.jpg" -o -name "*.html" -o -name "*.xml" -o -name "*.json" | while read file; do
                            if [ -f "$file" ]; then
                                cp "$file" test_results/
                                echo "Archived: $file"
                            fi
                        done
                        
                        # List archived files
                        echo "Archived test artifacts:"
                        ls -la test_results/ 2>/dev/null || echo "No test artifacts found"
                    '''
                }
            }
            post {
                always {
                    // Archive artifacts for later analysis
                    archiveArtifacts artifacts: 'test_results/**/*', allowEmptyArchive: true, fingerprint: true
                }
            }
        }
    }
    
    // Post-build actions with comprehensive cleanup and notifications
    post {
        always {
            script {
                echo "=== PIPELINE EXECUTION SUMMARY ==="
                echo "Build ID: ${env.BUILD_ID}"
                echo "Build URL: ${env.BUILD_URL}"
                echo "Duration: ${currentBuild.durationString}"
                echo "Result: ${currentBuild.result ?: 'SUCCESS'}"
                
                // Comprehensive workspace cleanup
                echo "Performing comprehensive workspace cleanup..."
                sh '''
                    # Deactivate virtual environment if active
                    deactivate 2>/dev/null || true
                    
                    # Remove virtual environment
                    if [ -d "${VENV_NAME}" ]; then
                        echo "Removing virtual environment: ${VENV_NAME}"
                        rm -rf "${VENV_NAME}"
                    fi
                    
                    # Clean up any temporary files
                    find . -name "*.pyc" -delete 2>/dev/null || true
                    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
                    
                    echo "Workspace cleanup completed"
                '''
            }
            
            // Final workspace cleanup
            deleteDir()
        }
        
        success {
            script {
                echo "🎉 SUCCESS: Selenium BrowserStack tests completed successfully!"
                echo "All test stages passed without errors."
                
                // Optional: Send success notification (uncomment if needed)
                // emailext (
                //     subject: "✅ Selenium Tests Passed - Build #${env.BUILD_NUMBER}",
                //     body: "The Selenium BrowserStack tests have completed successfully.\n\nBuild: ${env.BUILD_URL}",
                //     to: "${env.CHANGE_AUTHOR_EMAIL ?: 'team@example.com'}"
                // )
            }
        }
        
        failure {
            script {
                echo "❌ FAILURE: Selenium BrowserStack tests failed!"
                echo "Check the build logs and archived artifacts for detailed error information."
                echo "Build URL: ${env.BUILD_URL}"
                
                // Optional: Send failure notification (uncomment if needed)
                // emailext (
                //     subject: "❌ Selenium Tests Failed - Build #${env.BUILD_NUMBER}",
                //     body: "The Selenium BrowserStack tests have failed.\n\nPlease check the build logs: ${env.BUILD_URL}\n\nError details are available in the archived artifacts.",
                //     to: "${env.CHANGE_AUTHOR_EMAIL ?: 'team@example.com'}"
                // )
            }
        }
        
        unstable {
            echo "⚠️  WARNING: Pipeline completed with unstable results"
            echo "Some tests may have failed or encountered issues"
        }
        
        aborted {
            echo "🛑 ABORTED: Pipeline execution was cancelled"
            echo "The pipeline was manually aborted or timed out"
        }
    }
}