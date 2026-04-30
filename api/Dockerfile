#Stage1
FROM python:3.14-alpine as builder

WORKDIR /app


COPY . .

RUN pip install --upgrade pip \
&& pip install fastapi uvicorn pydantic requests

#Estage 2

FROM python:3.14-alpine



WORKDIR /app
# copia libs instaladas
COPY --from=builder /usr/local/lib/python3.14 /usr/local/lib/python3.14
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --from=builder /app  .

EXPOSE 8000

CMD ["python3","api.py"]