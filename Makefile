up:
	docker-compose up -d
	sleep 10

run:
	docker build -t rzd-analysis .
	docker run --rm --name my-spark-app -e ENABLE_INIT_DAEMON=false --link spark-master:spark-master --net rzd-analysis_default rzd-analysis

down:
	docker-compose down