%%Function to convert Thermister Resistance to Temperature
%This function converts the recorded thermister resistance into temperature
%using the extended Steinhart-Hart Equation.
%
%$$\frac{1}{T}=A+B\ln(\frac{r}{r_ref})+C\ln(\frac{r}{r_ref})^2+D\ln(\frac{r}{r_ref})^3$$
%
%This equation is then converted from Kelvin to Fahrenheit.
%
%$$T_fahrenheit=(T_kelvin-273.15)*1.8+32$$
%
%A, B, C and D are coeffficients depending on the type and model of the thermistor and the
%temperature range of interest. These coefficients were supplied by the
%termistor manufacturer.
%
%r_ref is the resistance of the resistor being used at ambient temperature
%25 degrees Celsius. The thermistor used is rated at 10,000 ohms.
function t=calculateTemperature(r)
A=3.354016E-3;
B=2.569850E-4;
C=2.620131E-6;
D=6.383091E-8;
r_ref=10000;

t_k=power(A+B*log(r/r_ref)+C*power(log(r/r_ref),2)+D*power(log(r/r_ref),3),-1);
t=(t_k-273.15)*1.8+32;