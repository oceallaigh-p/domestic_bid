# Flight Attendant Bid Calculation Program  
# &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; (Domestic Lines)

<br /> 

## Description

This is a simple Python program that calculates the total pay (hourly pay + per diem) for each line in a flight 
attendant bid packet. It then ranks the lines according to total pay (from greatest to least).


It uses pandas to read in data from Excel and uses pdfkit to produce a PDF document with the suggested
bid line order.

### Program Classes
```
class Line
        Attributes:
        line_number (int):   The monthly bid line number.
        credit      (int):   The total credit hours for the line.
        tafb        (int):   The 'time away from base' for the line.
        crew        (int):   The number of crew positions for the line.
        position    (str):   The position, FMP or FA, to bid for the line.
        pay         (float): The total pay value for the line (hourly + per diem).
```
```
class PurserLine
        Child of class Line.

        Attributes:
            Inherits from parent class.
            Sets position attribute to "FMP".
```
```
class FALine
        Child of class Line.

        Attributes:
            Inherits from parent class.
            Sets position attribute to "Any FA".
```

### Hardware
* iMac Pro
  * 10-core Intel Xenon Processor
  * 64 GB RAM (2666 MHz DDR4)
  * Radeon Pro Vega 56 8 GB

### Software Environment
* PyCharm 
	* Python 3.7
	* pandas 1.0.5
	* pdfkit 0.6.1

<br /> 
