BUILD_DIR:=build
VIRTUAL_ENV?=$(BUILD_DIR)/virtualenv

TEST_DIR:=test
MNT_DIR:=$(TEST_DIR)/mnt
REPO_DIR:=$(TEST_DIR)/repo
BARE_REPO:=$(TEST_DIR)/testing_repo.git
REPO:=$(TEST_DIR)/testing_repo

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

testenv: $(VIRTUAL_ENV)/bin/py.test

test: testenv
	mkdir -p $(TEST_DIR)
	mkdir -p $(MNT_DIR)
	mkdir -p $(REPO_DIR)
	mkdir -p $(BARE_REPO)
	cd $(BARE_REPO);\
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
	$(VIRTUAL_ENV)/bin/gitfs $(BARE_REPO) $(MNT_DIR) -o repos_path=$(REPO_DIR) &
	GITFS_PID=$!
	$(VIRTUAL_ENV)/bin/py.test tests
	kill -9 GITFS_PID


$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV)/bin/pip requirements.txt
	$(VIRTUAL_ENV)/bin/pip install cffi==0.8.6
	$(VIRTUAL_ENV)/bin/pip install -r requirements.txt
	touch $@

$(VIRTUAL_ENV)/bin/pip:
	virtualenv $(VIRTUAL_ENV)

clean:
	$(RM) -r $(BUILD_DIR)
	$(RM) -r $(TEST_DIR)

.PHONY: clean test testenv
