openapi-schema:
	python manage.py spectacular --color --file schema.yml

generate-secret-key:
	python -c "import secrets; print(secrets.token_urlsafe(64))"
