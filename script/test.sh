#!/bin/sh
export PATHONPATH=`pwd`
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest -v  > test_result/res.txt
coverage combine >> test_result/res.txt
coverage report >> test_result/res.txt
coverage html >> test_result/res.txt
mv htmlcov test_result
mv .coverage test_result
