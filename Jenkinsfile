pipeline {
  agent { docker { image 'markadams/chromium-xvfb-py3' } }
  stages {
    stage('Install Requirements') {
      steps {
        withEnv(overrides: ["HOME=${env.WORKSPACE}"]) {
          sh 'pip3 install --user -r requirements.txt'
          sh 'pip3 install --user -r requirements-dev.txt'
        }
      }
    }
    stage('Unit Test') {
      steps {
        withEnv(overrides: ["HOME=${env.WORKSPACE}"]) {
          sh 'python3 -m pytest -v --cov app/ --ignore=tests/FrontEnd'
        }
      }
      post {
        success {
          withEnv(["HOME=${env.WORKSPACE}"]) {
            sh '.local/bin/coverage xml'
            cobertura(coberturaReportFile: 'coverage.xml')
          }
        }
      }
    }
    stage('Front-End Chrome Tests') {
      steps {
        withEnv(overrides: ["HOME=${env.WORKSPACE}"]) {
          sh 'python3 -m pytest -v tests/FrontEnd'
        }
      }
    }
    stage('Lint') {
      steps {
        withEnv(overrides: ["HOME=${env.WORKSPACE}"]) {
          sh 'PYTHONPATH="." .local/bin/pylint app tests --load-plugins pylintplugins --exit-zero'
        }
      }

    }
  }
}
