#!/bin/bash

rm -rf test
mkdir -p test
mkdir -p test/12186_mnt
mkdir -p test/12852_repo
mkdir -p test/testing_repo.git
cat > test/.gitconfig <<EOF 
[user] 
       name = GitFs
       email = gitfs@gitfs.com\n

EOF

ROOT=`pwd`

cd test/testing_repo.git;\
    HOME=../../test git init --bare .;\
    cd ../../;\
    HOME=test git clone test/testing_repo.git test/testing_repo;\
    cd test/testing_repo;\
    echo "just testing around here" >> testing;\
    touch me;\
    HOME=../../test git add .;\
    HOME=../../test git commit -m "Initial test commit";\
    HOME=../../test git push -u origin master

echo "----------------------------"
cd $ROOT

gitfs test/testing_repo.git test/12186_mnt -o repo_path=test/12852_repo,fetch_timeout=2,merge_timeout=2,allow_other=true,log=/dev/null,idle_fetch_timeout=2

MOUNT_PATH=test/12186_mnt REPO_PATH=test/12852_repo REPO_NAME=testing_repo REMOTE=test/testing_repo py.test tests/integrations/current/test_write.py

pkill -f "gitfs test/testing_repo.git"
