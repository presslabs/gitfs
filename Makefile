BUILD_DIR:=build
VIRTUAL_ENV?=$(BUILD_DIR)/virtualenv

TEST_DIR:=test
MNT_DIR:=$(TEST_DIR)/$(shell bash -c 'echo $$RANDOM')_mnt
REPO_DIR:=$(TEST_DIR)/$(shell bash -c 'echo $$RANDOM')_repo
BARE_REPO:=$(TEST_DIR)/testing_repo.git
REPO:=$(TEST_DIR)/testing_repo
GITFS_PID:=$(TEST_DIR)/gitfs.pid

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

testenv: $(VIRTUAL_ENV)/bin/py.test

test: testenv
	mkdir -p $(TEST_DIR)
	mkdir -p $(MNT_DIR)
	mkdir -p $(REPO_DIR)
	mkdir -p $(BARE_REPO)
	cd $(BARE_REPO);\
		git config user.name "gitfs test";\
		git config user.email "gitfs@gitfs.com";\
		git init --bare .;\
		cd ../../;\
		git clone $(BARE_REPO) $(REPO);\
		cd $(REPO);\
		echo "just testing around here" >> testing;\
		touch me;\
		git add .;\
		git commit -m "Initial test commnit";\
		git push -u origin master
	pip install -e .
	$(VIRTUAL_ENV)/bin/gitfs $(BARE_REPO) $(MNT_DIR) -o repos_path=$(REPO_DIR) & echo "$$!" > $(GITFS_PID)
	$(VIRTUAL_ENV)/bin/py.test tests
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
