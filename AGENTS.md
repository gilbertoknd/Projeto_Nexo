# Diretrizes de Orquestração e Mapa de Documentação (Wiki)

Este projeto utiliza uma documentação modular em `/docs`.
**REGRA DE OURO:** Nenhum agente deve adivinhar nomes de campos, status ou rotas. Sempre leia o documento correspondente à sua função antes de gerar código.

## Mapa de Contexto por Agente
- **Agente DevOps (`Nemotron 3.5 Lightning`)**: Leia a seção de Infraestrutura abaixo.
- **Agente Backend (`Nemotron 3 Ultra`)**: Leia OBRIGATORIAMENTE `docs/01-DATA-AND-API.md` e `docs/02-ASYNC-AND-TESTS.md`.
- **Agente QA/Testes (`Flint 40B`)**: Leia OBRIGATORIAMENTE `docs/01-DATA-AND-API.md` e `docs/02-ASYNC-AND-TESTS.md`.
- **Agente Frontend (`GLM-5.3-Flash`)**: Leia OBRIGATORIAMENTE `docs/01-DATA-AND-API.md` e `docs/03-FRONTEND-SPEC.md`.

## Infraestrutura Base (Docker Compose)
- `db`: `postgres:15-alpine` (porta 5432)
- `rabbitmq`: `rabbitmq:3.12-management-alpine` (portas 5672 e 15672)
- `app`: Django + DRF (`python manage.py runserver 0.0.0.0:8000`)
- `worker`: `celery -A config worker -l info`
- `beat`: `celery -A config beat -l info`