docker-compose rm $(docker-compose ps -a -q)
docker-compose up --build
