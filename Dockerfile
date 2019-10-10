FROM python:3.7.4

WORKDIR /run/

COPY ./* /run/

RUN pip install --trusted-host pypi.python.org -r python_dependencies.txt

CMD ["python","python/scripts/monthly_report.py"]

