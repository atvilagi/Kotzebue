#TeX File Functions PuMA

#By Douglas Keller

def write_monthly_tex_var_file(Year_Month,Total_Usage,Fuel_Price,Fuel_per_Day,Total_Cost,Fuel_Cost_per_Day,Neighbor_Usage,Prog_Usage,Stove_ID,InT_Ave,OutT_Ave):
    
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
                 r'\newcommand{\outTave}{'+format(OutT_Ave,'.2f')+'}']
        
        for line in lines:
            tex_file.write(line)
            tex_file.write('\n')
            
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
\fancyfoot[C]{Flip page for tips to help you save on fuel!}
\fancyfoot[L]{\scriptsize{\stoveid}}
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
\begin{center}
\textbf{\Huge{Tips on Saving Fuel}}
\end{center}

\vspace{12pt}
\begin{itemize}
\item Tips go here
\end{itemize}

\end{document}
'''

    with open('monthly_report.tex','w') as tex_file:
        tex_file.write(text)