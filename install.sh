#!/bin/bash
cat > Dockerfile.thinker << E 
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY thinker/ ./thinker/
CMD ["python", "thinker/main.py"]
E
cat > Dockerfile.sister1 << E 
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY sister1/ ./sister1/
CMD ["python", "sister1/container_manager.py"]
E
cat > Dockerfile.notebook << E 
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY notebook/ ./notebook/
CMD ["python", "notebook/app.py"]
E
cat > Dockerfile.agent << E 
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY agent/ ./agent/
CMD ["python", "agent/enhanced_agent.py"]
E
docker build -t ai-agent-base:latest -f Dockerfile.agent .
docker-compose up --build -d
