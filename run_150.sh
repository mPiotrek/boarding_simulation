cnt=$(ls -1q ./pickle_dumps/* | wc -l)
while ((145 >= cnt))
do
	python3 ./runner.py
	cnt=$(ls -1q ./pickle_dumps/* | wc -l)
done
