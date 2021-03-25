pipeline {
    agent 'any'
    stages {
        stage('prepare') {
            steps {
                script {
                    println "project_name: ${project_name}"
                    println "code_dir: ${code_dir}"
                    println "server_hostname: ${server_hostname}"
                    println "server_ip_address: ${server_ip_address}"
                    println "server_passwd: ${server_passwd}"
                    println "build_variant: ${build_variant}"
                    println "build_sign: ${build_sign}"
                    println "build_verity: ${build_verity}"
                    println "build_action: ${build_action}"
                    println "need_publish: ${need_publish}"
                    println "devops_host_id: ${devops_host_id}"
                    println "devops_compile_id: ${devops_compile_id}"
                    println "is_new_project: ${is_new_project}"
                    println "is_test_pipeline: ${test_pipeline}"
                    println "is_test_host: ${test_host}"
                }
            }
        }
        stage('build') {
            steps {
                sh '''
                sshpass -p "$server_passwd" ssh -o StrictHostKeyChecking=no "$server_hostname@$server_ip_address" << EOF
                
                if [ ! -d "$code_dir" ]; then
                    echo "Project code directory does not exist!!!"
                    exit -1;
                fi
                
                cd "$code_dir"
                echo ""
                echo -------------------------------------------------
                echo code_dir: 
                pwd
                echo -------------------------------------------------
                echo ""
                
                if [ ! -f build.sh ]; then
                    echo "File build.sh does not exist!!!"
                    exit -2;
                fi
                
                if [ $test_pipeline == "true" ]; then
                    echo "Just test pipeline, exit."
                    exit 0
                fi
                bash build.sh "$project_name" "$build_variant" "$build_action" "$build_sign" "$build_verity" "$need_publish" "$devops_host_id" "$devops_compile_id" "$is_new_project" "$test_host"
                '''
            }
        }
    }
}