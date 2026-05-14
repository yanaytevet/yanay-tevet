docker run -v $(pwd)/../../yanay_tevet_backend:/usr/src/app -v logs:/var/log/yanay_tevet/ --rm -t \
    --network=yanay_tevet_network --name=yanay_tevet_backend_celery_beat yanay_tevet_backend celery -A yanay_tevet_backend beat \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler --settings=yanay_tevet_backend.dev_docker_settings
