all: monthly_reports

monthly_reports:
	python python/scripts/monthly_report.py
	cd reports/monthly; chmod +x monthly_reports.sh; ./monthly_reports.sh
