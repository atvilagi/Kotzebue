#TeX File Functions PuMA

#By Douglas Keller

def write_monthly_tex_var_file(Year_Month,Total_Usage,Fuel_Price,Fuel_per_Day,Total_Cost,Fuel_Cost_per_Day,Neighbor_Usage,Prog_Usage):
    
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
                 r'\newcommand{\progressmoreless}{'+PML+'}']
        
        for line in lines:
            tex_file.write(line)
            tex_file.write('\n')