.PHONY: nef-db-init help

nef-db-init: ## Populate the NEF Emulator with PoC scenario UEs and paths
	./scripts/nef_db_init.sh $(ARGS)

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
