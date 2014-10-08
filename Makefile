BUILD_DIR:=build
VIRTUAL_ENV?=$(BUILD_DIR)/virtualenv

TEST_DIR:=test
MNT_DIR:=$(TEST_DIR)/$(shell bash -c 'echo $$RANDOM')_mnt
REPO_DIR:=$(TEST_DIR)/$(shell bash -c 'echo $$RANDOM')_repo
REPO_NAME:=testing_repo
BARE_REPO:=$(TEST_DIR)/$(REPO_NAME).git
REMOTE:=$(TEST_DIR)/$(REPO_NAME)
GITFS_PID:=$(TEST_DIR)/gitfs.pid
GITCONFIG="\
[user]\n\
\t name = GitFs\n\
\t email = gitfs@gitfs.com\n"

GITCONFIG_PATH=$(TEST_DIR)/.gitconfig

all: $(BUILD_DIR)/pex

$(BUILD_DIR)/pex: $(BUILD_DIR) $(VIRTUAL_ENV)/bin/pex
	$(VIRTUAL_ENV)/bin/pex -r 'pygit2==0.21.3' -r 'fusepy==2.0.2' -s . -e gitfs:mount -o $(BUILD_DIR)/gitfs

$(VIRTUAL_ENV)/bin/pex: virtualenv
	$(VIRTUAL_ENV)/bin/pip install pex wheel

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV)/bin/pip
	@touch $@

$(VIRTUAL_ENV)/bin/pip:
	virtualenv $(VIRTUAL_ENV)

drone:
	sudo apt-get update
	sudo apt-get install -y software-properties-common python-software-properties
	sudo add-apt-repository -y ppa:presslabs/testing-ppa
	sudo apt-get update
	sudo apt-get install -y libgit2-0 libgit2-dev git git-core
	sudo chown ubuntu:admin /dev/fuse
	sudo chmod 660 /dev/fuse
	echo user_allow_other | sudo tee -a /etc/fuse.conf > /dev/null
	sudo chmod 644 /etc/fuse.conf

virtualenv: $(VIRTUAL_ENV)/bin/pip

testenv: virtualenv
	$(VIRTUAL_ENV)/bin/pip install -r test_requirements.txt
	mkdir -p $(TEST_DIR)
	mkdir -p $(MNT_DIR)
	mkdir -p $(REPO_DIR)
	mkdir -p $(BARE_REPO)
	echo $(GITCONFIG) > $(GITCONFIG_PATH)
	cd $(BARE_REPO);\
		HOME=../../$(TEST_DIR) git init --bare .;\
		cd ../../;\
		HOME=$(TEST_DIR) git clone $(BARE_REPO) $(REMOTE);\
		cd $(REMOTE);\
		echo "just testing around here" >> testing;\
		touch me;\
		HOME=../../$(TEST_DIR) git add .;\
		HOME=../../$(TEST_DIR) git commit -m "Initial test commit";\
		HOME=../../$(TEST_DIR) git push -u origin master

test: testenv
	$(VIRTUAL_ENV)/bin/pip install -e .
	$(VIRTUAL_ENV)/bin/gitfs $(BARE_REPO) $(MNT_DIR) -o repos_path=$(REPO_DIR) & echo "$$!" > $(GITFS_PID)
	sleep 2
	MOUNT_PATH=$(MNT_DIR) REPO_PATH=$(REPO_DIR) REPO_NAME=$(REPO_NAME) $(VIRTUAL_ENV)/bin/py.test tests
	kill -9 `cat $(GITFS_PID)`
	sudo umount -f $(MNT_DIR)

clean:
	rm -rf $(BUILD_DIR)
	rm -rf $(MNT_DIR)
	rm -rf $(REPO_DIR)
	rm -rf $(TEST_DIR)

.PHONY: clean test testenv virtualenv drone all
