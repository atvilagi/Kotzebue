
#Script to make the monthly reports from the python made tex files

for d in */
do

    cd $d
    pdflatex monthly_report_10_2019_${d%"/"}.tex
    mkdir -p ../../../output/puma_10_2019_monthly_reports_8_11_2019
    cp monthly_report_10_2019_${d%"/"}.pdf ../../../output/puma_10_2019_monthly_reports_8_11_2019/monthly_report_10_2019_${d%"/"}.pdf
    cd ../../../output/
    zip -r puma_10_2019_monthly_reports_8_11_2019.zip puma_10_2019_monthly_reports_8_11_2019/
    cp puma_10_2019_monthly_reports_8_11_2019.zip ../archived_data/puma_10_2019_monthly_reports_8_11_2019.zip
    cd ../reports/monthly/
done
