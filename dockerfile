# 1. Usar una imagen oficial de Python ligera
FROM python:3.12-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Evitar que Python escriba archivos .pyc y asegurar que los logs salgan de inmediato
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Instalar las dependencias del sistema necesarias (si las hubiera)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiar e instalar los requerimientos de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. Copiar el resto del código de la aplicación
COPY . .

# 7. Exponer el puerto en el que corre FastAPI
EXPOSE 8000

# 8. Comando para ejecutar la aplicación con Uvicorn en producción
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]