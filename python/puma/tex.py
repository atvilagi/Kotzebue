"""
TeX File Functions for PuMA

"""
import os
import numpy as np

def write_multimonth_tex_var_file(reportRange,Total_Usage,meanMonthly_Usage_per_Area,Fuel_per_Day,Total_Cost,Fuel_Cost_per_Day,Neighbor_mean_monthlyUsage_per_Area,Prog_Usage,Stove_ID,InT_Ave,annualCost, flagValue,daysMonitored,NeighborhoodSize,highMonths,tableRows,fuelPrice):
    """
    Writes a tex file with variables for the monthly report.

    Arguments:
        Year_Month -- year and month tuple
        Total_Usage -- total fuel usage in gallons
        meanMonthly_Usage_per_Area -- average fuel per month per square ft
        Fuel_Price -- current fuel price
        Fuel_per_Day -- fuel consumed per day
        Total_Cost -- total cost of fuel usage in dollars
        Fuel_Cost_per_Day -- fuel cost per day in dollars
        Neighbor_meanMonthlyUsage_per_area -- average fuel consumed per month per square foot by the other stoves
        Prog_Usage -- weather adjusted fuel consumption change percentage
        Stove_ID -- stove ID
        InT_Ave -- average indoor temperature during the month
        OutT_Ave -- average outdoor temperature during the month
        Tip_No -- tip index for the tip string list

    This function writes a tex file of all the given arguments as variables in tex format for the monthly report tex file to include and draw from.
    """

    histString = 'Your highest consumption months were '

    if len(highMonths) <1:
        highMonthString = ""
    elif (len(highMonths) == 1):
        highMonthString = 'Your highest consumption month was ' + highMonths[0]
    elif len(highMonths) == 2:
        highMonthString = histString + str(highMonths[0]) + ' and ' + str(highMonths[1]) + "."
    else:
        highMonthString = histString + ", ".join(highMonths[:-1]) + ' and ' + str(highMonths[-1]) + "."

    if flagValue == 1:
        flag = '*'
        qualifier = (' Total gallons extrapolated from {} days of measured data').format(str(daysMonitored))
    else:
        flag = ''
        qualifier = ''
    resultTable = []
    for row in tableRows:  # table rows is a list of tuples
        myList = [v.replace('$nan','--').replace('nan', '--') for v in row]
        if '--' in myList:
            myList = [myList[0]] + ['--' for v in myList[1:]]
        newRow= tuple(myList)
        resultTable.append(" & ".join(newRow))
    rows = r"\\".join(resultTable) + r"\\"
    if Stove_ID != 'FBK013':
        location_shown = "The location of your house is indicated with a triangle."
    else:
        location_shown = ""
    with open('multimonth_values.tex', 'w') as tex_file:  # opening and writing the tex file

        months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July',
                  'August', 'September', 'October', 'November', 'December']

        lines = [r'\newcommand{\totalusage}{' + '{:,.3f}'.format(Total_Usage) + flag + '}',
                 r'\newcommand{\fuelperday}{' + format(Fuel_per_Day, '.3f') + '}',
                r'\newcommand{\avemonthly}{' + format(meanMonthly_Usage_per_Area, '.3f') + '}',
                 r'\newcommand{\aveNmonthly}{' + '{:,.3f}'.format(Neighbor_mean_monthlyUsage_per_Area) + '}',
                 r'\newcommand{\totalcost}{' + '{:,.2f}'.format(Total_Cost) + '}',
                 r'\newcommand{\fuelcostperday}{' + '{:,.2f}'.format(Fuel_Cost_per_Day) + '}',

                 r'\newcommand{\reportstartmonth}{' + months[reportRange[0].month] + '}',
                 r'\newcommand{\reportstartyear}{' + str(reportRange[0].year) + '}',
                 r'\newcommand{\reportendmonth}{' + months[reportRange[-1].month] + '}',
                 r'\newcommand{\reportendyear}{' + str(reportRange[-1].year) + '}',

                 r'\newcommand{\stoveid}{' + Stove_ID + '}',
                 r'\newcommand{\inTave}{' + format(InT_Ave.mean(), '.2f') + '}',
                 r'\newcommand{\annualcost}{' + '{:,.2f}'.format(annualCost) + '}',
                 r'\newcommand{\neighborhoodsize}{' + str(NeighborhoodSize) + '}',
                 r'\newcommand{\daysmonitored}{' + str(daysMonitored) + '}',
                 r'\newcommand{\highmonths}{' + str(highMonthString) + '}',
                 r'\newcommand{\locationshown}{' + location_shown + '}',
                 r'\newcommand{\qualify}{' + flag + qualifier + '}',
                 r"""\newcommand\resultTable %
                { \begin
        {tabular}
       { | c|c|c|c|c|c|c|}
        \hline
        Month & \makecell
        {Average
        Daily\\
                Fuel\\
                Consumption\\ (g)\\} &  \makecell
        {Average \\Daily\\ Cost} &  \makecell
        {Monthly \\Total\\ Gallons} &  \makecell
        {Monthly \\Total\\ Cost} &  \makecell
        {Monthly \\Average\\ Indoor\\ Temperature\\ (F)} &  \makecell
        {Monthly \\Average\\ Outdoor\\ Tempearture\\ (F)} \\ [0.5ex]
        \hline\hline """ + rows + r' \hline \end {tabular} }',
                 r'\newcommand{\fuelprice}{' + str(format(fuelPrice, ',.2f')) + '}',]

        for line in lines:
            tex_file.write(line)
            tex_file.write('\n')
    return
def write_multimonth_tex_report_file(stove,current):
    '''
     Autogenerates the tex file for the individual stoves.

     This function just writes a tex file through python to allow for an easy and efficient way of producing the custome "nudge" reports quickly.
     :param: house the name of the house that metrics are based on
     :param: current is a pandas time range that the report covers

     :previous is a time range to compare to or None
     '''

    text = r'''
    %MultiMonth report for the PuMA fuel meter project
    %Created by T. Morgan

     \documentclass[12pt,a4paper]{article}

    \usepackage{fancyhdr,url,graphicx,caption,tabu,varwidth,gensymb}
    \usepackage[a4paper, top = 1in, bottom = 1in, left = .75in, right = .75in]{geometry}
    \usepackage{makecell}
    
      \fancyfoot{}
    \fancyhead{}
    \pagestyle{fancy}
    

\fancyfoot[C]{\scriptsize{UAF is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual: www.alaska.edu/nondiscrimination/.}}
   	   
\fancypagestyle{firstpage}{%
 \fancyhead[L]{\includegraphics[height = 32pt]{../../logos/acep.pdf}}
    		\fancyhead[R]{\includegraphics[height = 24pt]{../../logos/uaf_blue_hor.pdf}}
		\fancyfoot[C]{\scriptsize{Contact:
    		Dominique Pride, Principal Investigator: (907) 888-2613 or djpride@alaska.edu}\\
    		\vspace{6pt}
    		\tiny{If you have questions or concerns about your rights as a research participant, you can contact the UAF office of Research Integrity\\
   		 at 474-7800 (Fairbanks area) or 1-866-7800 (toll-free outside the Fairbanks area) or uaf-irb@alaska.edu}
  }
    		
 		 \fancyfoot[R]    {\tiny{\stoveid}}
}
   
    \setlength{\parindent}{0pt}
    \setlength{\fboxrule}{.8pt}
    \usepackage[font = footnotesize, textfont=it, labelfont= bf]{caption}

    \input{multimonth_values}

    \begin{document}
    \thispagestyle{firstpage}

    \begin{center}
    \textbf{\Huge{\\{\reportstartyear} - {\reportendyear}\\
      \vspace{8pt}
      Fuel Usage Report}}
       \end{center}

    \begin{center}  
   
   \vspace{8pt}

    \begin{tabu}[m]{llX[m,m]}

  \begin{minipage}{3in}
  
 
    \begin{varwidth}{1\textwidth}
    \large
     Thank you for participating!
    You were one of {\neighborhoodsize} houses contributing information to this study. 
    Below is some information on your fuel consumption between {\reportstartmonth} {\reportstartyear} and {\reportendmonth} {\reportendyear}.
    \end{varwidth}
   
\end{minipage}
 
   &&  
  \begin{minipage}{\linewidth}
 \vspace{6pt}  
\textbf{\large{\underline{ Summary:}\vspace{6pt} }} \\
   \vspace{3pt}
Total Usage: {\totalusage} gal\\
   \vspace{3pt}
Total Days Monitored: {\daysmonitored}\\
   \vspace{3pt}
Average Indoor Temperature: {\inTave} {\degree}F\\
   \vspace{3pt}
Total Cost: \${\totalcost}**\\
   \vspace{3pt}
\underline{Average Annual Cost: \${\annualcost}}\\

\tiny{\qualify}\\
 \tiny{**Total cost estimates are based on a static fuel price of \${\fuelprice} per gallon.}
\end{minipage}
  
 \end{tabu} 
   \end{center}
   
  \vspace{8pt}
\begin{center}
    \textbf{\large{Mean Daily Fuel Consumption During\\
 Cold Weather Months}}\\
     \includegraphics[height= 3in]{spatial_fuel.png}\\ 
     \end{center}
     \begin{varwidth}{1\textwidth}
     \large
     {The figure above is a color shaded map showing the estimated average daily gallons of fuel oil used per square foot within the study area during September through April. Consumption estimates were produced using data collected from all participants in the Fairbanks North Star Borough using generalized linear models based on latitude, logitude, slope, elevation and aspect. {\locationshown}}
 \end{varwidth}
\vspace{4pt}
\newpage
\begin{center} 
  \textbf{\large{Mean Fuel Consumption per Area}}\\     
       \includegraphics[height= 2.5in]{fuel_usage.png}\\
         
\end{center}  
  \begin{varwidth}{1\textwidth}
     \large
     {Standardizing the rate of fuel consumption per square foot permits comparison between homes of different sizes.
      The figure above shows how your consumption rate (red) compares to other participants of this study (orange) during each year of this study. 
      }
 \end{varwidth}
    \vspace{4pt}
    
    \begin{center}
   
   
    \textbf{\large{Annual Fuel Consumption and Mean Monthly Temperature}}\\
    \vspace{4pt}
    \includegraphics[height= 3in]{monthly_track_your_progress.png}\\
    \end{center}
 
       \begin{varwidth}{1\textwidth}

      \large{The figure above shows your monthly fuel consumption rate and the mean monthly temperature over the study period. 
      The bars show the gallons of fuel you consumed per heating degree day.
       Gallons per heating degree day is the number of gallons of fuel used in a month divided by the total number of 
        heating degree days in the month. Heating degree days are used to adjust for the weather when comparing fuel usage across 
        different months. The lines show the average temperature for the month. The color of bars and lines corresponds to the calendar year.}\\
    \end{varwidth}
    \newpage
    
    \vspace{8pt}
    \begin{center}
    \small
     {\highmonths}{ }\\
     \vspace{16pt}
    \textbf{\large{Your Home's Fuel Usage for the Duration of This Study}}\\
    \vspace{16pt}
    {\resultTable}\\
    \end{center}
    \vspace{4pt}
   
       \begin{varwidth}{1\textwidth}

      \large{The table above shows your average daily fuel consumption, average daily fuel cost, monthly total gallons consumed, monthly total cost, monthly average indoor temperature and the monthly average outdoor temperature for the duration of the study. Missing entries correspond to periods when the fuel meter was down or when your stove was not in use. All cost estimates are based on a static fuel price of \${\fuelprice} per gallon.}
    \end{varwidth}
    \newpage
    \begin{minipage}{\linewidth}
     \begin{varwidth}{1\textwidth}

      \large{The figure below shows your average fuel consumption for each hour of the day by season. The different colors correspond to the seasons.}
    \end{varwidth}
       

    \begin{center} 
   \textbf{\large{Your Seasonal Diurnal Fuel Consumption Pattern}}\\
  \textbf{\small{  (Gallons per Hour)  }}\\       
       \includegraphics[height= 3in]{seasonal_polar_plot.png}\\
\end{center}  
       \begin{varwidth}{1\textwidth}

      \large{
      Many factors can affect the amount of fuel required to keep your home comfortable. 
      Indoor temperature settings affect overall fuel requirements. 
      Below is your estimated cost based on average daily outdoor temperature for the range of indoor temperatures we recorded for your home.
      The colors correspond to different indoor temperatures. The higher the indoor temperature setting, the greater the heating cost per day. 
      As can been seen in the graphic below, this effect is amplified as the outdoor temperature decreases.}
       \end{varwidth}

    \begin{center}
      \textbf{\large{Predicted Fuel Cost}}\\
     \textbf{\small{(based on a mean fuel price of \$3.50 per gallon)}}\\
    \vspace{16pt}
    \includegraphics[height= 3.2in]{gamm.png}\\

    \end{center}

    \end{minipage}
    \end{document}
    '''  # tex text

    with open('multimonth_report_' + str(current[0].strftime("%Y_%b")) + '_' + str(
            current[-1].strftime("%Y_%b")) + '_' + stove + '.tex', 'w') as tex_file:  # writing the text to the tex file
        tex_file.write(text)
    return

def write_monthly_tex_var_file(reportRange,Total_Usage,Total_Usage_per_Area,meanMonthly,NeighborhoodMeanMonthly,Total_Cost,Fuel_Cost_per_Day,Neighbor_Usage_per_Area,Prog_Usage,Stove_ID,InT_Ave,OutT_Ave,YearlyCost,flagValue,daysMonitored,NeighborhoodSize ):
    """
    Writes a tex file with variables for the monthly report.
    
    Arguments:
        Year_Month -- year and month tuple
        Total_Usage -- total fuel usage in gallons
        Total_Usage_per_Area -- fuel per square ft
        Fuel_Price -- current fuel price
        Fuel_per_Day -- fuel consumed per day
        Total_Cost -- total cost of fuel usage in dollars
        Fuel_Cost_per_Day -- fuel cost per day in dollars
        Neighbor_Usage -- fuel consumed by the other stoves
        Prog_Usage -- weather adjusted fuel consumption change percentage
        Stove_ID -- stove ID
        InT_Ave -- average indoor temperature during the month
        OutT_Ave -- average outdoor temperature during the month
        Tip_No -- tip index for the tip string list
        
    This function writes a tex file of all the given arguments as variables in tex format for the monthly report tex file to include and draw from.
    """
    
    Percent_Usage = abs((Total_Usage_per_Area - Neighbor_Usage_per_Area)/Neighbor_Usage_per_Area) #determining percent difference in consumption between stove of interest and their neighbors
    if Total_Usage_per_Area > Neighbor_Usage_per_Area:
        ML = 'more'
    else:
        ML = 'less'
    
    if Prog_Usage > 0:
        PML = 'more'
    elif Prog_Usage < 0:
        PML = 'less'
    elif Prog_Usage == 0:
        Prog_Usage = 1
        PML = 'more/less'
    elif np.isnan(Prog_Usage):
        return
    
    Prog_Usage = abs(Prog_Usage) #percentagizing the progress of usage


    if flagValue == 1:
         flag = '**'
         qualifier = (' Total gallons extrapolated from {} days of measured data.').format(str(daysMonitored))
    else:
        flag=''
        qualifier = ''

    with open('monthly_values.tex','w') as tex_file: #opening and writing the tex file
        
        months = ['','January','February','March','April','May','June','July',
              'August','September','October','November','December']
        
        lines = [r'\newcommand{\totalusage}{'+format(Total_Usage,'.2f') + flag + '}',
                 r'\newcommand{\neighborhoodsize}{' + str(NeighborhoodSize) +'}',
                 r'\newcommand{\daysmonitored}{' + str(daysMonitored) +'}',
                 r'\newcommand{\avemonthly}{'+format(meanMonthly,',.2f')+'}',
                 r'\newcommand{\aveNmonthly}{'+format(NeighborhoodMeanMonthly,',.2f')+'}',
                 r'\newcommand{\totalcost}{'+format(Total_Cost,',.2f')+'}',
                 r'\newcommand{\percentusage}{'+format(Percent_Usage*100,'.2f')+'}',
                 r'\newcommand{\moreless}{'+ML+'}',
                 r'\newcommand{\reportstartmonth}{'+months[reportRange[0].month]+'}',
                 r'\newcommand{\reportstartyear}{'+str(reportRange[0].year)+'}',
                 r'\newcommand{\reportendmonth}{' + months[reportRange[-1].month] + '}',
                 r'\newcommand{\reportendyear}{' + str(reportRange[-1].year) + '}',
                 r'\newcommand{\progress}{'+format(Prog_Usage*100,'.2f')+'}',
                 r'\newcommand{\progressmoreless}{'+PML+'}',
                 r'\newcommand{\stoveid}{'+Stove_ID+'}',
                 r'\newcommand{\inTave}{'+ format(InT_Ave.values[0], '.2f')+'}',
                 r'\newcommand{\yearlycost}{'+format(YearlyCost, ',.2f')+'}',
                 r'\newcommand{\qualify}{' + flag + qualifier + '}',]
        
        for line in lines:
            tex_file.write(line)
            tex_file.write('\n')

def report_tips(n):
    """
    Function holding the list of tips for the monthly reports.
    
    Arguments:
        n -- tip index
        
    Returns:
        tip of interest
    
    This function just makes an easy way to select a tip for each new report to come out for the stoves owners to be "nudged."
    """
    
    tips = readTips()
    return tips[n]
def readTips():
    #current path
    file_path = os.path.abspath(os.path.dirname(__file__))
    #relative path to file
    file = os.path.join(*[file_path,'..','..','data','text','tips.txt'])
    #read
    f = open(file, 'r')
    tips = f.readlines()
    f.close()
    #return as list
    return tips

def write_monthly_tex_report_file(stove,current,previous=None):
    '''
    Autogenerates the tex file for the individual stoves.

    This function just writes a tex file through python to allow for an easy and efficient way of producing the custome "nudge" reports quickly.
    :param: house the name of the house that metrics are based on
    :param: current is a pandas time range that the report covers
    :previous is a time range to compare to or None
    '''

    if previous is None:
        comment = '%'
    else:
        comment = ''

    if stove == 'FBK044': #no inT data?
        inT_txt = r''
    else:
       	inT_txt = r'Your average indoor temperature for this month was: {\inTave} {\degree}F\\'

    text = r'''
%Monthly report for the PuMA fuel meter project
%Created by Doug Keller
        
\documentclass[12pt,a4paper]{article}
\usepackage{fancyhdr,url,graphicx,caption,tabu,varwidth,gensymb}
\usepackage[a4paper, top = 1in, bottom = 1in, left = .75in, right = .75in]{geometry}
\renewcommand{\familydefault}{\sfdefault}
\fancyfoot{}
\fancyhead{}
\pagestyle{fancy}
\fancyhead[L]{\includegraphics[height = 32pt]{../../logos/acep.pdf}}
\fancyhead[R]{\includegraphics[height = 24pt]{../../logos/uaf_blue_hor.pdf}}
\fancyfoot[C]{\scriptsize{Contact:
Dominique Pride, Principal Investigator: (907) 888-2613 or djpride@alaska.edu}\\
\vspace{6pt}
\tiny{If you have questions or concerns about your rights as a research participant, you can contact the UAF office of Research Integrity\\
at 474-7800 (Fairbanks area) or 1-866-7800 (toll-free outside the Fairbanks area) or uaf-irb@alaska.edu}}
\fancyfoot[R]{\tiny{\stoveid}}
\renewcommand{\headrulewidth}{0pt}
\setlength{\parindent}{0pt}
\setlength{\fboxrule}{.8pt}
\usepackage[font = footnotesize, textfont=it, labelfont= bf]{caption}
\input{monthly_values}
\begin{document}
\begin{center}
\textbf{\Huge{\\{\reportmonth} {\reportyear} Fuel Usage Report}}
\end{center}
\begin{center}
\fbox{
\begin{varwidth}{.8\textwidth}
In {\reportmonth} you consumed {\percentusage}\% {\moreless} gal/ft$^2$ than your neighbors.
\end{varwidth}
}
\end{center}
\vspace{8pt}
\begin{tabu}[c]{llX[m,c]}
\begin{minipage}{4in}
\includegraphics[height = 2.375in]{monthly_fuel_usage.png}
\end{minipage}
 && 
\begin{minipage}{\linewidth}
\underline{{\reportmonth} {\reportyear} Fuel Usage:}\\
Total Usage: {\totalusage} gal\\
Price of Fuel: \${\fuelprice}/gal\\
Total Cost: \${\totalcost}\\
\newline
\tiny{\qualify}
\end{minipage}
\end{tabu}
\rule{\textwidth}{1pt}
\newline
\begin{tabu}{X[m,c]X[m,c]}
\begin{minipage}{\linewidth}
\underline{In {\reportmonth:}}\\
Your average fuel consumption for heating was {\fuelperday} gallons per day.\\
Your average fuel cost for heating was \${\fuelcostperday} per day.\\
'''+inT_txt+r'''
The average outdoor temperature for this month was: {\outTave} {\degree}F\\
\end{minipage}
&
\begin{minipage}{\linewidth}
\includegraphics[height = 3in]{monthly_polar_plot.png}
\end{minipage}
\end{tabu}
\rule{\textwidth}{1pt}
\underline{Track Your Progress:}\\
'''+comment+r'''You consumed {\progress}\% {\progressmoreless} this month than last month.\\
\begin{center}
\includegraphics[height= 1.75in]{monthly_track_your_progress.png}\\
\tiny{*gal/HDD is the number of gallons of fuel used in a month divided by the total number of heating degree days in the month. Heating degree days for a given day are calculated by subtracting the day's average temperature from the base temperature of 65 {\degree}F.}
\end{center}
\newpage
\renewcommand{\headsep}{14pt}
\fancyfoot{}
\fancyfoot[C]{\scriptsize{UAF is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual: www.alaska.edu/nondiscrimination/.}}
\begin{center}
\textbf{\Huge{Tip to Save Fuel}}
\end{center}
\vspace{75pt}
\begin{center}
\begin{minipage}{.85\linewidth}
{\tips}
\end{minipage}
\end{center}
\end{document}
''' #tex text

    with open('monthly_report_'+str(current[0].strftime("%Y_%b"))+'_'+str(current[-1].strftime("%Y_%b"))+'_'+stove+'.tex','w') as tex_file: #writing the text to the tex file
        tex_file.write(text)