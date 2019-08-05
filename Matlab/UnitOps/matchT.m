function M= matchT( file, month )
% Matches monthly outside temperature to file time 
%   Detailed explanation goes here
[x,y]=size(month);
[f,g]=size(file);
for b=1:x
for a =1:f
if (file.Hr(a)==month.Hr(b)) && (file.DD(a)==month.Day(b))
file.T_o(a)=month.T(b);
end
end
end

end

