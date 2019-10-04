"""
Bash Script Functions for PuMA

By Douglas Keller
"""

from datetime import datetime

def bash_monthly_reports(year_month):
    """
    Function that writes a bash script to create a unique monthly report zipfile
    
    Arguments:
        year_month -- year and month in a tuple (year,month)
    """
    
    now = datetime.now()
    file = 'monthly_report_'+str(year_month[1])+'_'+str(year_month[0])+'_'
    total_file = 'puma_'+str(year_month[1])+'_'+str(year_month[0])+'_monthly_reports_'+str(now.day)+'_'+str(now.month)+'_'+str(now.year)
    
    text = r'''
#Script to make the monthly reports from the python made tex files

for d in */
do

    cd $d
    pdflatex '''+file+r'''${d%"/"}.tex
    mkdir -p ../../../output/'''+total_file+r'''
    cp '''+file+r'''${d%"/"}.pdf ../../../output/'''+total_file+r'''/'''+file+r'''${d%"/"}.pdf
    cd ../../../output/
    zip -r '''+total_file+r'''.zip '''+total_file+r'''/
    cp '''+total_file+r'''.zip ../archived_data/'''+total_file+r'''.zip
    cd ../reports/monthly/
done
'''

    with open('monthly_reports.sh','w') as bash_script:
        bash_script.write(text)