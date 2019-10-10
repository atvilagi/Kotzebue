all: unified_netcdf monthly_reports

unified_netcdf:
	python3 python/scripts/puma_text_to_unified.py

monthly_reports:
	python3 python/scripts/monthly_report.py
	cd reports/monthly; chmod +x monthly_reports.sh; ./monthly_reports.sh

clean_monthly_reports:
	rm -r reports/monthly/*
	rm -r output/*
