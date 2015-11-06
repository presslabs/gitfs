PREFIX:=/usr/local
BUILD_DIR:=build
VIRTUAL_ENV?=$(BUILD_DIR)/virtualenv

TESTS?=tests
TEST_DIR?=test
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

all: $(BUILD_DIR)/gitfs

install: $(BUILD_DIR)/gitfs
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	install -m 0755 $(BUILD_DIR)/gitfs $(DESTDIR)$(PREFIX)/bin/gitfs

uninstall:
	rm -rf $(DESTDIR)$(PREFIX)/bin/gitfs

$(BUILD_DIR)/gitfs: $(BUILD_DIR) $(VIRTUAL_ENV)/bin/pex
	$(VIRTUAL_ENV)/bin/pex -r 'fusepy==2.0.2' -r 'pygit2==0.22.0' -r 'atomiclong==0.1.1' -s . -e gitfs:mount -o $(BUILD_DIR)/gitfs

$(VIRTUAL_ENV)/bin/pex: virtualenv
	$(VIRTUAL_ENV)/bin/pip install pex wheel

$(VIRTUAL_ENV)/bin/mkdocs: virtualenv
	$(VIRTUAL_ENV)/bin/pip install mkdocs

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV)/bin/pip
	@touch $@

$(VIRTUAL_ENV)/bin/pip:
	virtualenv --setuptools $(VIRTUAL_ENV)

virtualenv: $(VIRTUAL_ENV)/bin/pip

testenv: virtualenv
	$(VIRTUAL_ENV)/bin/pip install cffi
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
	$(VIRTUAL_ENV)/bin/gitfs $(BARE_REPO) $(MNT_DIR) -o repo_path=$(REPO_DIR),fetch_timeout=2,merge_timeout=2,allow_other=true,foreground=true,log=/dev/null,idle_fetch_timeout=2 & echo "$$!" > $(GITFS_PID)
	sleep 2
	MOUNT_PATH=$(MNT_DIR) REPO_PATH=$(REPO_DIR) REPO_NAME=$(REPO_NAME) REMOTE=$(REMOTE) $(VIRTUAL_ENV)/bin/py.test --cov-report term-missing --cov gitfs $(TESTS)
	kill -9 `cat $(GITFS_PID)`
	sudo umount -f $(MNT_DIR)

clean:
	rm -rf $(BUILD_DIR)
	rm -rf $(TEST_DIR)

docs: $(VIRTUAL_ENV)/bin/mkdocs
	$(VIRTUAL_ENV)/bin/mkdocs build

.PHONY: clean test testenv virtualenv drone all
