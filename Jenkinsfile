pipeline {
  agent {
    docker { image 'python:3-alpine' }
  }
  stages {
    stage("Install Requirements") {
      steps {
        withEnv(["HOME=${env.WORKSPACE}"]) {
          sh 'pip install --user -r requirements.txt'
          sh 'pip install --user -r requirements-dev.txt'
        }
      }
    }
    stage("Test") {
      steps {
        withEnv(["HOME=${env.WORKSPACE}"]) {
          sh 'python -m pytest -v --cov app/'
        }
      }
      post {
        success {
          withEnv(["HOME=${env.WORKSPACE}"]) {
            sh '.local/bin/coverage xml'
            cobertura coberturaReportFile: 'coverage.xml'
          }
        }
      }
    }
    stage("Lint") {
      steps {
        withEnv(["HOME=${env.WORKSPACE}"]) {
          sh 'PYTHONPATH="." .local/bin/pylint app tests --load-plugins pylintplugins'
        }
      }
    }
  }
}
