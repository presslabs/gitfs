PREFIX:=/usr/local
BUILD_DIR:=build
VIRTUAL_ENV?=$(BUILD_DIR)/virtualenv

TESTS:=tests
TEST_DIR:=/tmp/gitfs-tests
MNT_DIR:=$(TEST_DIR)/$(shell bash -c 'echo $$RANDOM')_mnt
REPO_DIR:=$(TEST_DIR)/$(shell bash -c 'echo $$RANDOM')_repo
REPO_NAME:=testing_repo
BARE_REPO:=$(TEST_DIR)/$(REPO_NAME).git
export
REMOTE:=$(TEST_DIR)/$(REPO_NAME)
GITFS_PID:=$(TEST_DIR)/gitfs.pid
GIT_NAME=GitFs
GIT_EMAIL=gitfs@gitfs.com

all: $(BUILD_DIR)/gitfs

install: $(BUILD_DIR)/gitfs
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	install -m 0755 $(BUILD_DIR)/gitfs $(DESTDIR)$(PREFIX)/bin/gitfs

uninstall:
	rm -rf $(DESTDIR)$(PREFIX)/bin/gitfs

$(BUILD_DIR)/gitfs: $(BUILD_DIR) $(VIRTUAL_ENV)/bin/pex
	$(VIRTUAL_ENV)/bin/pex -v --disable-cache -r requirements.txt -e gitfs:mount -o $(BUILD_DIR)/gitfs .

$(VIRTUAL_ENV)/bin/pex: virtualenv
	$(VIRTUAL_ENV)/bin/pip install pex wheel

$(VIRTUAL_ENV)/bin/mkdocs: virtualenv
	$(VIRTUAL_ENV)/bin/pip install mkdocs

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV)/bin/pip
	@touch $@

$(VIRTUAL_ENV)/bin/pip:
	virtualenv --setuptools $(VIRTUAL_ENV) -ppython3.4

virtualenv: $(VIRTUAL_ENV)/bin/pip

testenv: virtualenv
	script/testenv

test: testenv
	script/test

clean:
	rm -rf $(BUILD_DIR)
	rm -rf $(TEST_DIR)

.PHONY: docs
docs: $(VIRTUAL_ENV)/bin/mkdocs
	$(VIRTUAL_ENV)/bin/mkdocs build --clean

.PHONY: gh-pages
gh-pages: docs
	git config --global user.email "bot@presslabs.com"
	git config --global user.name "Igor Debot"
	cp docs/index.html .
	git add .
	echo -n "(autodoc) " > /tmp/COMMIT_MESSAGE ; git log -1 --pretty=%B >> /tmp/COMMIT_MESSAGE ; echo >> /tmp/COMMIT_MESSAGE ; echo "Commited-By: $$CI_BUILD_URL" >> /tmp/COMMIT_MESSAGE
	git commit -F /tmp/COMMIT_MESSAGE

.PHONY: clean test testenv virtualenv drone all
