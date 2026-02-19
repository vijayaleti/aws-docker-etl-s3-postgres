INFRA_DIR := infra

.PHONY: infra-init infra-plan infra-apply infra-destroy \
        etl-extract etl-transform etl-all \
        docker-up docker-down clean

infra-init:
	@cd $(INFRA_DIR) && terraform init

infra-plan:
	@cd $(INFRA_DIR) && terraform plan

infra-apply:
	@cd $(INFRA_DIR) && terraform apply

infra-destroy:
	@cd $(INFRA_DIR) && terraform destroy

etl-extract:
	@docker compose run --rm etl_extract

etl-transform:
	@docker compose run --rm etl_transform

etl-all: etl-extract etl-transform

docker-up:
	@docker compose up -d db

docker-down:
	@docker compose down

clean: docker-down
	@cd $(INFRA_DIR) && rm -f terraform.tfstate terraform.tfstate.backup

