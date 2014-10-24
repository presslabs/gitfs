#!/bin/bash

MIN_REPO_CNT=1
MAX_REPO_CNT=25

clone-repos() {
    for ((idx=MIN_REPO_CNT; idx <= MAX_REPO_CNT; idx++)); do
        echo "Mounting repo no. $idx"
        rm -rf /tmp/gitfs$idx/*; mkdir -p /tmp/gitfs$idx/mnt; mkdir -p /tmp/gitfs$idx/repo ; gitfs $REPOS_SERVER_SSH_DETAILS/home/manu/test-repos/repo$idx/ /tmp/gitfs$idx/mnt -o repo_path="/tmp/gitfs$idx/repo",foreground=False,debug=False
    done
}

touch-files() {
    for ((repo_cnt=MIN_REPO_CNT; repo_cnt <= MAX_REPO_CNT; repo_cnt++)); do
        echo "Touching file in repo $repo_cnt"
        touch /tmp/gitfs$repo_cnt/mnt/current/a
        #sleep 1s
        echo "Removing the file from the repo $repo_cnt"
        rm /tmp/gitfs$repo_cnt/mnt/current/a
    done
}

unmount-repos() {
    for ((idx=MIN_REPO_CNT; idx <= MAX_REPO_CNT; idx++)); do
        echo "Unmounting repo no. $idx"
        sudo umount -f /tmp/gitfs$idx/mnt
    done
}

git-log-cnt() {
    for ((repo_cnt=MIN_REPO_CNT; repo_cnt <= MAX_REPO_CNT; repo_cnt++)); do
        cd /tmp/gitfs$repo_cnt/repo/
        commits_cnt=$(git log | grep commit | wc -l)
        echo "Repo $repo_cnt, No. of commits: $commits_cnt"
        echo
    done
}

create-repos-on-server() {
    for ((repo_cnt=MIN_REPO_CNT; repo_cnt <= MAX_REPO_CNT; repo_cnt++)); do
        mkdir repo$repo_cnt
        git init --bare ./repo$repo_cnt
    done
}

$@


