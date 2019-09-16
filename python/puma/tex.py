#TeX File Functions PuMA

#By Douglas Keller

def write_monthly_tex_var_file(Year_Month,Total_Usage,Fuel_Price,Fuel_per_Day,Total_Cost,Fuel_Cost_per_Day,Neighbor_Usage,Prog_Usage,Stove_ID,InT_Ave,OutT_Ave,Tip_No):
    
    Percent_Usage = abs(1 - Total_Usage/Neighbor_Usage)
    if Total_Usage > Neighbor_Usage:
        ML = 'more'
    else:
        ML = 'less'
    
    if Prog_Usage > 1:
        PML = 'more'
    else:
        PML = 'less'
    
    Prog_Usage = abs(1 - Prog_Usage)
    
    with open('monthly_values.tex','w') as tex_file:
        
        months = ['','January','February','March','April','May','June','July',
              'August','September','October','November','December']
        
        lines = [r'\newcommand{\totalusage}{'+format(Total_Usage,'.3f')+'}',
                 r'\newcommand{\fuelperday}{'+format(Fuel_per_Day,'.3f')+'}',
                 r'\newcommand{\fuelprice}{'+format(Fuel_Price,'.2f')+'}',
                 r'\newcommand{\totalcost}{'+format(Total_Cost,'.2f')+'}',
                 r'\newcommand{\fuelcostperday}{'+format(Fuel_Cost_per_Day,'.2f')+'}',
                 r'\newcommand{\neighborusage}{'+format(Neighbor_Usage,'.3f')+'}',
                 r'\newcommand{\percentusage}{'+format(Percent_Usage*100,'.2f')+'}',
                 r'\newcommand{\moreless}{'+ML+'}',
                 r'\newcommand{\reportmonth}{'+months[Year_Month[1]]+'}',
                 r'\newcommand{\reportyear}{'+str(Year_Month[0])+'}',
                 r'\newcommand{\progress}{'+format(Prog_Usage*100,'.2f')+'}',
                 r'\newcommand{\progressmoreless}{'+PML+'}',
                 r'\newcommand{\stoveid}{'+Stove_ID+'}',
                 r'\newcommand{\inTave}{'+format(InT_Ave,'.2f')+'}',
                 r'\newcommand{\outTave}{'+format(OutT_Ave,'.2f')+'}',
                 r'\newcommand{\tips}{'+report_tips(Tip_No)+'}']
        
        for line in lines:
            tex_file.write(line)
            tex_file.write('\n')

def report_tips(n):
    
    tips = ['Consider reducing the set temperature on your heater. A one degree reduction in your set temperature results in about 2\% savings on your fuel bill. The U.S. Department of Energy recommends setting your temperature to 68 degrees when you are at home and awake, and recommends turning down the temperature (by as much as 10 degrees) during the nighttime hours when you are asleep or when you are away from your home. (http://alaskarenewableenergy.org/index.php/2019/07/18/2019-energy-savers-tips-published/)','In cold climates, a great deal of heat can be lost through your windows during the winter. Using transparent interior plastic film over your windows can improve the thermal efficiency of your home. In a study conducted by the Cold Climate Housing Research Center, inexpensive interior plastic film improved the insulation of the tested window by 33\%. (http://www.cchrc.org/evaluating-window-insulation)','Space heating accounts for 77\% of household energy costs in Interior Alaska. Air leaks around your windows and doors let cold air into your home. Don’t let your heat escape. Check around your windows and doors for air leaks, and use weather stripping and caulk to stop any air leaks. (www.energystar.com)','Heat rises. Reversing the direction of a ceiling fan to run clockwise on low speed in the winter forces warm air near the ceiling down into the living space. This may allow you to reduce your set temperature by a few degrees saving you fuel and money. (www.energystar.com)','After the sun goes down, closing your shades and drapes helps reduce heat loss from your windows. Insulated blinds, referred to as honeycomb or cellular shades, use pockets of inert air to increase the thermal efficiency of your windows. In a study conducted by the Cold Climate Housing Research Center, insulated blinds improved the insulation of the tested window by 60\%. (http://www.cchrc.org/evaluating-window-insulation)','Air leaks in attics, basements, and crawlspaces can result in a substantial loss of heat. Holes or gaps around vents, pipes, and electrical wires let heat out and drafts in, causing you to burn more fuel to heat your home. Seal small gaps with caulk and holes up to three inches in diameter with spray foam to stop air leaks. (www.energystar.gov)','Direct vent heaters, such as Toyostoves and Monitor heaters, are very fuel efficient heating appliances. To assure that your heater is running at its maximum efficiency, make sure to have it serviced at least every other year. Maintenance issues such as cracked gaskets can reduce the fuel efficiency of your heater, meaning you have to use more fuel to heat your home. Regular maintenance can add years to the life of your heater and reduces the odds of your heater breaking down in the middle of winter.']
    
    return tips[n]

def write_monthly_tex_report_file():

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
In {\reportmonth} you consumed {\percentusage}\% {\moreless} than your neighbors.
\end{varwidth}
}
\end{center}

\vspace{12pt}

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
\end{minipage}


\end{tabu}

\rule{\textwidth}{1pt}
\newline

\begin{tabu}{X[m,c]X[m,c]}

\begin{minipage}{\linewidth}
\underline{In {\reportmonth:}}\\

Your average fuel consumption was {\fuelperday} gallons per day.\\

Your average fuel cost was \${\fuelcostperday} per day\\

Average indoor and outdoor temperatures for this month are: {\inTave} {\degree}F and {\outTave} {\degree}F, respectively.\\
\end{minipage}

&

\begin{minipage}{\linewidth}
\includegraphics[height = 3in]{monthly_polar_plot.png}
\end{minipage}


\end{tabu}

\rule{\textwidth}{1pt}
\newline

\underline{Track Your Progress:}\\

You consumed {\progress}\% {\progressmoreless} this month than last month.\\
\begin{center}
\includegraphics[height= 1.875in]{monthly_track_your_progress.png}
\end{center}

\newpage
\renewcommand{\headsep}{14pt}
\fancyfoot{}
\fancyfoot[C]{\scriptsize{UAF is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual: www.alaska.edu/nondiscrimination/.}}
\begin{center}
\textbf{\Huge{Tip to Save Fuel}}
\end{center}

\vspace{36pt}
{\tips}

\end{document}
'''

    with open('monthly_report.tex','w') as tex_file:
        tex_file.write(text)