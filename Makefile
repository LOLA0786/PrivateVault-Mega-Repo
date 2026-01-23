
.PHONY: install

install:
	@echo "✅ install"
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt
