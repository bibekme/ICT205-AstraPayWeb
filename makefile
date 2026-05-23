.PHONY: app waf

app:
	docker compose -f docker-compose.yml -d $(filter-out $@,$(MAKECMDGOALS))

waf:
	docker compose -f docker-compose-waf.yml  -d $(filter-out $@,$(MAKECMDGOALS))

%:
	@: