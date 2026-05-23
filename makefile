.PHONY: app-up app-down waf-up waf-down status pull

app-up:
	docker compose -f docker-compose.yml up -d

app-down:
	docker compose -f docker-compose.yml down

waf-up:
	docker compose -f docker-compose-waf.yml up -d

waf-down:
	docker compose -f docker-compose-waf.yml down

pull:
	git pull

status:
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"