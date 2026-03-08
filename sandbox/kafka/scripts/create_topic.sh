docker exec kafka /kafka/bin/kafka-topics.sh \
  --create \
  --topic asset \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1