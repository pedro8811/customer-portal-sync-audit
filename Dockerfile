FROM python:3.11-alpine

WORKDIR /app

# Copia o código fonte para dentro do container
COPY src/ /app/src/

# Expõe a porta do servidor nativo do Python
EXPOSE 8000

# Executa o script
CMD ["python", "src/main.py"]