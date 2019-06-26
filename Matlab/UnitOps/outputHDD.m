function x=outputHDD(Table1,min1, max1, Table2,min2, max2)
while min1<max1
while min2<max2
if Table2.Time(min2)==Table1.Var4(min1)
Table2.Var15(min2)=Table1.HeatingDegreeHours(min1);
end
min2=min2+1;
end
min1=min1+1;
end