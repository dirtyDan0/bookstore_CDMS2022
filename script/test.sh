#!/bin/sh
export PATHONPATH=`pwd`
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest -v --ignore=fe/data > not_upload/res.txt
coverage combine >> not_upload/res.txt
coverage report >> not_upload/res.txt
coverage html >> not_upload/res.txt
mv htmlcov not_upload
mv .coverage not_upload
