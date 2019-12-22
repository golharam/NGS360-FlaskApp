pipeline {
  agent any
  stages {
    stage('Test') {
      agent { dockerfile true }
      steps {
        sh 'python -m pytest tests'
      }
    }
  } 
  post {
    always {
        sh 'docker system prune -f -a --volumes'
    }
  }
}

