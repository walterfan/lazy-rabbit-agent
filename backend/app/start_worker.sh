#!/bin/bash

set -o errexit
set -o nounset

#celery -A main.celery worker --loglevel=info
#cd ../deploy && docker-compose -f docker-compose-test.yml up -d
celery -A worker.celery_app worker --loglevel=INFO -E
