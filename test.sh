#!/bin/bash

rm -rf test
mkdir -p test
mkdir -p test/mount_point
mkdir -p test/gitfs_owned_repo
mkdir -p test/origin.git
cat > test/.gitconfig <<EOF 
[user] 
       name = GitFs
       email = gitfs@gitfs.com\n

EOF

ROOT=`pwd`

cd test/origin.git;\
    HOME=../../test git init --bare .;\
    cd ../../;\
    HOME=test git clone test/origin.git test/dev_repo;\
    cd test/dev_repo;\
    echo "just testing around here" >> testing;\
    touch me;\
    HOME=../../test git add .;\
    HOME=../../test git commit -m "Initial test commit";\
    HOME=../../test git push -u origin master

echo "----------------------------"
cd $ROOT

gitfs test/origin.git test/mount_point -o repo_path=test/gitfs_owned_repo,fetch_timeout=2,merge_timeout=2,allow_other=true,log=log.txt,debug=true,idle_fetch_timeout=2

MOUNT_PATH=test/mount_point REPO_PATH=test/gitfs_owned_repo REPO_NAME=dev_repo REMOTE=test/dev_repo py.test --capture=no
pkill -f "gitfs test/origin.git"
