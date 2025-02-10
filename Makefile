run-telegram-agent:
	python telegram_agent.py
run-chat-agent-api:
	bash runserver.sh

start-stg:
	python -m pip install -r requirements.txt
	pm2 reload app.stg.json --update-env

stop-stg:
	pm2 stop stg.raidenx-agent

delete-stg:
	pm2 delete stg.raidenx-agent

start-prod:
	python -m pip install -r requirements.txt
	pm2 reload app.prod.json --update-env

stop-prod:
	pm2 stop prod.raidenx-agent

delete-prod:
	pm2 delete prod.raidenx-agent
