FROM python:3.12-slim AS build
WORKDIR /lab
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY proto ./proto
COPY scripts/generate_proto.py ./scripts/generate_proto.py
RUN python scripts/generate_proto.py

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /lab
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=build /lab/kuksa ./kuksa
COPY sdv_lab ./sdv_lab
COPY tests/__init__.py tests/smoke_live.py ./tests/
USER 10001:10001
ENTRYPOINT ["python", "-m", "sdv_lab"]
CMD ["advisor", "--broker", "broker:55555"]
