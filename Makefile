BUILD_DIR:=build
VIRTUAL_ENV?=$(BUILD_DIR)/virtualenv

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

testenv: $(VIRTUAL_ENV)/bin/py.test

test: testenv
	$(VIRTUAL_ENV)/bin/py.test tests

$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV)/bin/pip requirements.txt
	$(VIRTUAL_ENV)/bin/pip install cffi==0.8.6
	$(VIRTUAL_ENV)/bin/pip install -r requirements.txt
	touch $@

$(VIRTUAL_ENV)/bin/pip:
	virtualenv $(VIRTUAL_ENV)

clean:
	$(RM) -r $(BUILD_DIR)

.PHONY: clean test testenv
