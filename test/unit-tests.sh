nohup /workdir/tr_ocr &
apt-get update && apt-get install curl -y
curl -X POST localhost:8090/api/tr-run -d '{"img": "" }'
