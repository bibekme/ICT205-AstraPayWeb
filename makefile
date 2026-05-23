.PHONY: app waf

app:
	docker compose -f docker-compose.yml $(filter-out $@,$(MAKECMDGOALS)) -d 

waf:
	docker compose -f docker-compose-waf.yml  $(filter-out $@,$(MAKECMDGOALS)) -d 

%:
	@: