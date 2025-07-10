pipeline {
    agent any

    // 파라미터 정의
    parameters {
        string(name: 'RESTORE_VERSION', defaultValue: '', description: '복원할 버전 (MMddHHmm 형식, 예: 06251130)')
        booleanParam(name: 'RESTORE_MODE', defaultValue: false, description: '복원 모드를 활성화하려면 체크')
    }

    // Jenkins 파이프라인에서 사용할 환경 변수
    environment {
        // Docker Registry 설정
        DOCKER_REGISTRY = 'registry.lyckabc.xyz'
        IMAGE_NAME = 'sabangnet-api'
        DOMAIN = 'lyckabc.xyz'
        DEV_DOMAIN = 'lyckabc.xyz'
        SUBDOMAIN = 'api'
        // Git 설정
        GIT_REPO_URL = 'https://github.com/GopediaPro/sabangnet_API.git'
        GIT_CREDENTIAL_ID = 'Iv23likhQak519AdkG6d'
        
        // 인증 정보
        REGISTRY_CREDENTIAL_ID = 'docker-registry-credentials'
        SSH_CREDENTIAL_ID = 'lyckabc-ssh-key-id'
        DOCKER_REGISTRY_ID = 'docker-registry-id'
        DOCKER_REGISTRY_PW = 'docker-registry-pw'
        SABANGNET_ENV_FILE = 'sabangnet-env-file'
        SABANGNET_ENV_FILE_DEV = 'sabangnet-env-file-dev'
        DOCKER_COMPOSE_FILE_ID = 'sabangnet-docker-compose-file'
        DOCKER_COMPOSE_ENV_FILE_ID = 'sabangnet-docker-compose-env-file'
        
        // 배포 서버 설정 (브랜치별로 동적 설정)
        DEPLOY_SERVER_PORT = '50022'
        
        // 브랜치별 설정을 위한 변수
        IS_DEPLOYABLE = "${env.BRANCH_NAME in ['main', 'dev'] || env.BRANCH_NAME.contains('docker') ? 'true' : 'false'}"
        // Docker 이미지 태그용 안전한 브랜치명 (슬래시를 하이픈으로 변환)
        DOCKER_SAFE_BRANCH_NAME = "${env.BRANCH_NAME.replaceAll('/', '-')}"
    }

    stages {
        stage('Environment Setup') {
            steps {
                script {
                    echo "🔍 현재 브랜치: ${env.BRANCH_NAME}"
                    
                    // 브랜치별 환경 설정
                    if (env.BRANCH_NAME == 'main') {
                        env.DEPLOY_ENV = 'production'
                        env.DEPLOY_SERVER_USER_HOST = 'root@lyckabc.xyz'
                    } else if (env.BRANCH_NAME == 'dev') {
                        env.DEPLOY_ENV = 'development'
                        env.DEPLOY_SERVER_USER_HOST = 'root@lyckabc.xyz'
                        env.DOMAIN = DEV_DOMAIN
                    } else if (env.BRANCH_NAME.contains('docker')) {
                        env.DEPLOY_ENV = 'development'
                        env.DEPLOY_SERVER_USER_HOST = 'root@lyckabc.xyz'
                        env.DOMAIN = DEV_DOMAIN
                        DOCKER_SAFE_BRANCH_NAME = "docker"
                        echo "🐳 Docker 브랜치 감지: ${env.BRANCH_NAME}"
                    } else {
                        env.DEPLOY_ENV = 'none'
                        echo "⚠️ 브랜치 '${env.BRANCH_NAME}'는 자동 배포 대상이 아닙니다."
                    }
                    
                    // PR 빌드인지 확인
                    if (env.CHANGE_ID) {
                        echo "📋 PR #${env.CHANGE_ID} 빌드 - 배포 없이 빌드만 수행합니다."
                        env.IS_PR_BUILD = 'true'
                    } else {
                        env.IS_PR_BUILD = 'false'
                    }
                }
            }
        }

        stage('Initialize') {
            steps {
                script {
                    if (params.RESTORE_MODE) {
                        if (params.RESTORE_VERSION.trim().isEmpty()) {
                            error "❌ 복원 모드에서는 'RESTORE_VERSION'을 반드시 입력해야 합니다."
                        }
                        env.IMAGE_TAG = params.RESTORE_VERSION
                        echo "🔄 [복원 모드] 버전 ${env.IMAGE_TAG}(으)로 복원을 시작합니다."
                    } else {
                        def now = new Date()
                        def timestamp = now.format('MMddHHmm', TimeZone.getTimeZone('Asia/Seoul'))
                        
                        // 브랜치명을 태그에 포함
                        if (env.BRANCH_NAME == 'main') {
                            env.IMAGE_TAG = "prod-${timestamp}"
                        } else if (env.BRANCH_NAME == 'dev') {
                            env.IMAGE_TAG = "dev-${timestamp}"
                        } else if (env.BRANCH_NAME.contains('docker')) {
                            env.IMAGE_TAG = "docker-${timestamp}"
                        } else {
                            env.IMAGE_TAG = "etc-${timestamp}"
                        }
                        
                        echo "🚀 [빌드 모드] 새 버전 ${env.IMAGE_TAG}(을)를 생성합니다."
                    }
                }
            }
        }

        stage('Checkout from Git') {
            when {
                not { expression { params.RESTORE_MODE } }
            }
            steps {
                echo 'Source 코드를 다운로드합니다...'
                checkout scm
            }
        }

        stage('Code Quality Check') {
            when {
                allOf {
                    not { expression { params.RESTORE_MODE } }
                    expression { env.IS_PR_BUILD == 'true' || env.IS_DEPLOYABLE == 'true' }
                }
            }
            parallel {
                stage('Lint') {
                    steps {
                        echo "코드 린팅을 수행합니다..."
                        // sh 'flake8 .'
                        // sh 'black --check .'
                        // sh 'isort --check-only .'
                        // sh 'mypy .'
                    }
                }
                stage('Test') {
                    steps {
                        echo "테스트를 수행합니다..."
                        // sh 'pytest --maxfail=1 --disable-warnings'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when {
                allOf {
                    not { expression { params.RESTORE_MODE } }
                    anyOf {
                        expression { env.IS_PR_BUILD == 'true' }
                        expression { env.IS_DEPLOYABLE == 'true' }
                    }
                }
            }
            steps {
                script {
                    echo "Docker 이미지를 빌드합니다: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.IMAGE_TAG}"
                    echo "Docker 이미지를 빌드합니다: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${DOCKER_SAFE_BRANCH_NAME}-latest"
                    
                    // 브랜치별 환경 파일 선택
                    def envFileCredentialId = SABANGNET_ENV_FILE
                    if (env.BRANCH_NAME == 'dev') {
                        envFileCredentialId = SABANGNET_ENV_FILE_DEV  // 개발용 환경 파일
                    }
                    
                    withCredentials([file(credentialsId: envFileCredentialId, variable: 'ENV_FILE')]) {
                        sh "cp ${ENV_FILE} .env"
                    }
                    
                    // Docker 이미지 빌드
                    sh """
                        docker build \
                            --build-arg BUILD_ENV=${env.DEPLOY_ENV} \
                            --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                            --build-arg BUILD_VERSION=${env.IMAGE_TAG} \
                            --build-arg VCS_REF=\$(git rev-parse --short HEAD) \
                            -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.IMAGE_TAG} \
                            -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${DOCKER_SAFE_BRANCH_NAME}-latest \
                            .
                    """
                    // .env 파일 삭제
                    sh "rm -f .env"
                }
            }
        }

        stage('Security Scan') {
            when {
                allOf {
                    not { expression { params.RESTORE_MODE } }
                    expression { env.IS_DEPLOYABLE == 'true' }
                }
            }
            steps {
                echo "Docker 이미지 보안 스캔을 수행합니다..."
                // Trivy, Anchore 등의 도구를 사용한 보안 스캔
                // sh "trivy image ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.IMAGE_TAG}"
            }
        }

        stage('Push to Private Registry') {
            when {
                allOf {
                    not { expression { params.RESTORE_MODE } }
                    expression { env.IS_DEPLOYABLE == 'true' }
                    expression { env.IS_PR_BUILD == 'false' }
                }
            }
            steps {
                script {
                    echo "Private Registry에 로그인 및 이미지 푸시를 시작합니다..."
                    
                    withCredentials([usernamePassword(
                        credentialsId: REGISTRY_CREDENTIAL_ID,
                        usernameVariable: 'REGISTRY_USER',
                        passwordVariable: 'REGISTRY_PASS'
                    )]) {
                        sh """
                            echo \${REGISTRY_PASS} | docker login ${DOCKER_REGISTRY} -u \${REGISTRY_USER} --password-stdin
                            
                            # 버전 태그와 latest 태그 모두 푸시
                            docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.IMAGE_TAG}
                            docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${DOCKER_SAFE_BRANCH_NAME}-latest
                            
                            docker logout ${DOCKER_REGISTRY}
                        """
                    }
                }
            }
        }

        stage('Deploy to Server') {
            when {
                allOf {
                    expression { env.IS_DEPLOYABLE == 'true' }
                    expression { env.IS_PR_BUILD == 'false' }
                    anyOf {
                        expression { params.RESTORE_MODE == true }
                        not { expression { params.RESTORE_MODE } }
                    }
                }
            }
            steps {
                echo "배포 서버(${DEPLOY_SERVER_USER_HOST})에 ${env.DEPLOY_ENV} 환경으로 배포를 시작합니다..."
                
                sshagent(credentials: [SSH_CREDENTIAL_ID]) {
                    script {
                        // 브랜치별 환경 파일 선택
                        def envFileCredentialId = SABANGNET_ENV_FILE
                        if (env.BRANCH_NAME == 'dev') {
                            envFileCredentialId = SABANGNET_ENV_FILE_DEV  // 개발용 환경 파일
                        }
                        
                        withCredentials([
                            file(credentialsId: envFileCredentialId, variable: 'ENV_FILE'),
                            file(credentialsId: DOCKER_COMPOSE_FILE_ID, variable: 'DOCKER_COMPOSE_FILE'),
                            file(credentialsId: DOCKER_COMPOSE_ENV_FILE_ID, variable: 'DOCKER_COMPOSE_ENV_FILE'),
                            usernamePassword(
                                credentialsId: REGISTRY_CREDENTIAL_ID,
                                usernameVariable: 'REGISTRY_USER',
                                passwordVariable: 'REGISTRY_PASS'
                            )
                        ]) {
                            // 환경 파일 내용을 변수에 저장
                            def envFileContent = sh(
                                script: "cat ${ENV_FILE}",
                                returnStdout: true
                            ).trim()
                            
                            def dockerComposeFileContent = sh(
                                script: "cat ${DOCKER_COMPOSE_FILE}",
                                returnStdout: true
                            ).trim()
                            
                            def dockerComposeEnvFileContent = sh(
                                script: "cat ${DOCKER_COMPOSE_ENV_FILE}",
                                returnStdout: true
                            ).trim()
                            
                            sh """
                                ssh -p ${DEPLOY_SERVER_PORT} -o StrictHostKeyChecking=no ${DEPLOY_SERVER_USER_HOST} << 'EOF'
                                set -e
                                
                                echo ">> 배포 디렉토리로 이동"
                                cd /morphogen/neunexus/sabangnet_api
                                
                                echo ">> 백업 디렉토리 생성"
                                mkdir -p ./backup
                                
                                echo ">> 이전 버전 백업"
                                BACKUP_TIMESTAMP=\$(date +%Y%m%d%H%M%S)
                                RAND_CHAR=\$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 1 | head -n 1)
                                if [ -f .env ]; then
                                    cp .env ./backup/.env.backup.\${BACKUP_TIMESTAMP}${RAND_CHAR}
                                fi
                                if [ -f .env.docker ]; then
                                    cp .env.docker ./backup/.env.docker.backup.\${BACKUP_TIMESTAMP}${RAND_CHAR}
                                fi
                                if [ -f docker-compose.yml ]; then
                                    cp docker-compose.yml ./backup/docker-compose.yml.backup.\${BACKUP_TIMESTAMP}${RAND_CHAR}
                                fi
                                
                                echo ">> 배포용 환경변수 파일(.env) 생성"
                                cat > .env << 'ENV_EOF'
${envFileContent}
ENV_EOF
                                
                                echo ">> Docker Compose 환경변수 파일(.env.docker) 생성"
                                cat > .env.docker << 'DOCKER_ENV_EOF'
${dockerComposeEnvFileContent}
IMAGE_TAG=${env.IMAGE_TAG}
DEPLOY_ENV=${env.DEPLOY_ENV}
DOCKER_ENV_EOF
                                
                                echo ">> Docker Compose 파일(docker-compose.yml) 생성"
                                cat > docker-compose.yml << 'COMPOSE_EOF'
${dockerComposeFileContent}
COMPOSE_EOF
                                
                                echo ">> Docker Registry 로그인 (비대화형)"
                                echo '${REGISTRY_PASS}' | docker login ${DOCKER_REGISTRY} -u '${REGISTRY_USER}' --password-stdin
                                
                                echo ">> 최신 버전의 Docker 이미지를 다운로드합니다: ${env.IMAGE_TAG}"
                                docker compose --env-file .env.docker pull
                                
                                echo ">> 헬스체크를 위한 이전 컨테이너 정보 저장"
                                OLD_CONTAINER_ID=\$(docker compose --env-file .env.docker ps -q ${IMAGE_NAME} 2>/dev/null || true)
                                
                                echo ">> docker-compose를 사용하여 서비스 업데이트"
                                docker compose --env-file .env.docker up -d --force-recreate --no-build   
                                
                                echo ">> 헬스체크 수행 (30초 대기)"
                                sleep 30
                                
                                # 간단한 헬스체크 (실제 환경에 맞게 수정 필요)
                                if docker compose --env-file .env.docker ps | grep -q "Up"; then
                                    echo "✅ 배포 성공: ${env.IMAGE_TAG}"
                                    
                                    # 이전 이미지 정리 (최근 3개 버전만 유지)
                                    echo ">> 오래된 Docker 이미지 정리"
                                    docker images ${DOCKER_REGISTRY}/${IMAGE_NAME} --format "{{.Tag}} {{.ID}}" | \\
                                        grep -E "^(dev|prod|docker)-[0-9]{8}" | \\
                                        sort -r | \\
                                        tail -n +4 | \\
                                        awk '{print \$2}' | \\
                                        xargs -r docker rmi || true
                                else
                                    echo "❌ 헬스체크 실패, 롤백을 시도합니다..."
                                    if [ ! -z "\$OLD_CONTAINER_ID" ]; then
                                        # 최신 백업 파일로 롤백
                                        LATEST_BACKUP=\$(ls -t ./backup/.env.docker.backup.* 2>/dev/null | head -1)
                                        if [ ! -z "\$LATEST_BACKUP" ]; then
                                            cp "\$LATEST_BACKUP" .env.docker
                                            docker compose --env-file .env.docker up -d --force-recreate --no-build
                                        fi
                                    fi
                                    exit 1
                                fi
                                
                                docker logout ${DOCKER_REGISTRY}
EOF
                            """
                        }
                    }
                }
            }
        }

        stage('Post-Deploy Verification') {
            when {
                allOf {
                    expression { env.IS_DEPLOYABLE == 'true' }
                    expression { env.IS_PR_BUILD == 'false' }
                    not { expression { params.RESTORE_MODE } }
                }
            }
            steps {
                echo "배포 후 검증을 수행합니다..."
                // E2E 테스트, API 헬스체크 등
                script {
                    def deployUrl = env.BRANCH_NAME == 'main' ? 
                        "https://${SUBDOMAIN}.${DOMAIN}" : 
                        "https://${SUBDOMAIN}.${DOMAIN}"
                    
                    // sh "curl -f ${deployUrl}/health || exit 1"
                }
            }
        }
    }

    post {
        always {
            echo 'Jenkins Agent의 Workspace를 정리합니다...'
            
            // Docker 이미지 정리 (PR 빌드의 경우)
            script {
                if (env.IS_PR_BUILD == 'true') {
                    sh """
                        docker rmi ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.IMAGE_TAG} || true
                        docker rmi ${DOCKER_REGISTRY}/${IMAGE_NAME}:${DOCKER_SAFE_BRANCH_NAME}-latest || true
                    """
                }
            }
            
            cleanWs()
        }
        
        success {
            script {
                if (env.IS_DEPLOYABLE == 'true' && env.IS_PR_BUILD == 'false') {
                    // Slack, Email 등으로 배포 성공 알림
                    echo "✅ ${env.DEPLOY_ENV} 환경에 버전 ${env.IMAGE_TAG} 배포 성공!"
                }
            }
        }
        
        failure {
            script {
                if (env.IS_DEPLOYABLE == 'true' && env.IS_PR_BUILD == 'false') {
                    // Slack, Email 등으로 배포 실패 알림
                    echo "❌ ${env.DEPLOY_ENV} 환경 배포 실패!"
                }
            }
        }
    }
}