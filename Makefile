.PHONY: status check-sensitive preflight

status:
	git status --short --branch

check-sensitive:
	sh scripts/check-sensitive-files.sh

preflight:
	sh scripts/preflight.sh
