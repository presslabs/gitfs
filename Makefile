BUILD_DIR:=build
VIRTUAL_ENV?=$(BUILD_DIR)/virtualenv

TEST_DIR:=test
MNT_DIR:=$(TEST_DIR)/$(shell bash -c 'echo $$RANDOM')_mnt
REPO_DIR:=$(TEST_DIR)/$(shell bash -c 'echo $$RANDOM')_repo
BARE_REPO:=$(TEST_DIR)/testing_repo.git
REPO:=$(TEST_DIR)/testing_repo
GITFS_PID:=$(TEST_DIR)/gitfs.pid
GITCONFIG="\
[user]\n\
\t name = GitFs\n\
\t email = gitfs@gitfs.com\n"

GITCONFIG_PATH=$(TEST_DIR)/.gitconfig

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

testenv: $(VIRTUAL_ENV)/bin/py.test

test: testenv
	ls /dev
	mkdir -p $(TEST_DIR)
	mkdir -p $(MNT_DIR)
	mkdir -p $(REPO_DIR)
	mkdir -p $(BARE_REPO)
	echo $(GITCONFIG) > $(GITCONFIG_PATH)
	cd $(BARE_REPO);\
		HOME=../../$(TEST_DIR) git init --bare .;\
		cd ../../;\
		HOME=$(TEST_DIR) git clone $(BARE_REPO) $(REPO);\
		cd $(REPO);\
		echo "just testing around here" >> testing;\
		touch me;\
		HOME=../../$(TEST_DIR) git add .;\
		HOME=../../$(TEST_DIR) git commit -m "Initial test commnit";\
		HOME=../../$(TEST_DIR) git push -u origin master
	pip install -e .
	$(VIRTUAL_ENV)/bin/gitfs $(BARE_REPO) $(MNT_DIR) -o repos_path=$(REPO_DIR) & echo "$$!" > $(GITFS_PID)
	sleep 2
	MOUNT_PATH=$(MNT_DIR) REPO_PATH=$(REPO_DIR) $(VIRTUAL_ENV)/bin/py.test tests
	kill -9 `cat $(GITFS_PID)`

$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV)/bin/pip requirements.txt
	$(VIRTUAL_ENV)/bin/pip install cffi==0.8.6
	$(VIRTUAL_ENV)/bin/pip install -r requirements.txt
	touch $@

$(VIRTUAL_ENV)/bin/pip:
	virtualenv $(VIRTUAL_ENV)

clean:
	rm -rf $(BUILD_DIR)
	rm -rf $(MNT_DIR)
	rm -rf $(REPO_DIR)
	rm -rf $(TEST_DIR)

.PHONY: clean test testenv
