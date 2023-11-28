FROM python:3.8-slim-buster
WORKDIR /app
ADD . /app
RUN python -m pip install --no-cache-dir -r requirements.txt
ENV IMAGE_VERSION=0.0.1
CMD ["python", "rules_generator.py"]