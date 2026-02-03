# Kafka

```sh
  kafka-consumer-groups --bootstrap-server localhost:9092 --describe --all-groups
```

```sh
  docker-compose down -v
```

```sh
  docker compose down --remove-orphans
  docker compose up -d
```

```sh
docker exec -it kafka kafka-topics \
  --create \
  --topic asset.ingestion \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```
