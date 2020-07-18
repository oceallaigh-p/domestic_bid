import pandas as pd
import pdfkit as pdf


class Line(object):
    """
    This is a class for flight attendant bid lines.

    Attributes:
        line_number (int):   The monthly bid line number.
        credit      (int):   The total credit hours for the line.
        tafb        (int):   The 'time away from base' for the line.
        crew        (int):   The number of crew positions for the line.
        position    (str):   The position, FMP or FA, to bid for the line.
        pay         (float): The total pay value for the line (hourly + per diem).
    """

    PAY_RATE = 65.79 / 60.0  # Pay rate per minute
    FMP_RATE = 1.0 / 60.0  # Purser pay rate per minute
    PER_DIEM_RATE = 0.04  # Per diem rate per minute
    GUARANTEE = 70 * 60  # Monthly guaranteed credit (in minutes)

    def __init__(self, line_number, credit, tafb, crew, position=None):
        """
        The constructor for the Line class.

        Parameters:
            line_number (int):   The monthly bid line number.
            credit      (int):   The total credit hours for the line.
            tafb        (int):   The 'time away from base' for the line.
            crew        (int):   The number of crew positions for the line.
            position    (str):   The position, FMP or FA, to bid for the line.
        """

        self.line_number = int(line_number)
        self.credit = int(self.__convert_minutes(credit))
        self.tafb = int(self.__convert_minutes(tafb))
        self.crew = int(crew)
        self.position = position
        self.pay = self.__calculate_pay()

    def __eq__(self, other):
        """
        Tests equality of pay for two Line objects.

        Parameter:
            other (Line): The other Line object to which self is being compared.

        Returns:
            (bool): Returns True if the pay for the two objects are equal.
        """

        return self.pay == other.pay

    def __lt__(self, other):
        """
        Tests whether the pay for object self is less than the pay for object other.

        Parameter:
            other (Line): The other Line object to which self is being compared.

        Returns:
            (bool): Returns True if the pay for object self is less than the pay for object other.
        """

        return self.pay < other.pay

    @staticmethod
    def __convert_minutes(time):
        """
        Converts a string for time into an integer (in minutes).

        Parameter:
            time (str):  A string that represents time with a format of hours.minutes.

        Returns:
            (int): An integer for time in minutes.
        """

        hours, minutes = str(time).split('.')

        return int(hours) * 60 + (int(minutes) * 10 if len(minutes) == 1 else int(minutes))

    def __calculate_pay(self):
        """
        Calculates the total line pay (hours plus per diem) for the month.

        It calculates pay based in the following:
            - if credit hours < contractual minimum guaranteed hours,
                  minimum guaranteed hours is used
            - if credit hours >= contractual minimum guaranteed hours,
                  credit hours is used
            -- if position is FMP, Purser pay is added to the pay for the line

        Returns:
            (float): The total line pay (hourly + per diem + purser pay [if applicable])
        """

        if self.credit < self.GUARANTEE:
            pay = self.GUARANTEE * self.PAY_RATE + self.tafb * self.PER_DIEM_RATE
        else:
            pay = self.credit * self.PAY_RATE + self.tafb * self.PER_DIEM_RATE

        if self.position == 'FMP':
            return pay + self.credit * self.FMP_RATE
        else:
            return pay

    def as_dict(self):
        """
        Used to create a dictionary to be used by pandas DataFrame constructor.

        Is called to create output file of the data we are interested in.

        Returns:
            (Line): Dictionary containing line number, position, and total pay

        Reference:
        https://stackoverflow.com/questions/47623014/converting-a-list-of-objects-to-a-pandas-dataframe
        """

        return {'Line Number': self.line_number, 'Position': self.position, 'Total Pay': self.pay}


class PurserLine(Line):
    """
    This is a class for Purser bid lines.

    It is a child of class Line that sets the position attribute to FMP.
    """

    def __init__(self, line_number, credit, tafb, crew):
        Line.__init__(self, line_number, credit, tafb, crew, position='FMP')


class FALine(Line):
    """
    This is a class for Flight Attendant bid lines.

    It is a child of class Line that sets the position attribute to Any FA.
    """

    def __init__(self, line_number, credit, tafb, crew):
        Line.__init__(self, line_number, credit, tafb, crew, position='Any FA')


def color_position_lines(d):
    """
    Function that sets the color of the line based on position type (FMP or Any FA).

    It colors the line orange if it is a purser line and blue if it is a flight
    attendant line.

    Reference:
        https://kanoki.org/2019/01/02/pandas-trick-for-the-day-color-code-columns-rows-cells-of-dataframe/
    """

    if d.Position == 'FMP':
        return ['background-color: orange'] * 3
    else:
        return ['background-color: blue'] * 3


def style_df(df_bid):
    """
    Function that sets the CSS properties to style the pandas DataFrame.

    Reference:
        https://mode.com/example-gallery/python_dataframe_styling/
    """

    # Set CSS properties for th elements (header) in pandas DataFrame
    th_props = [
        ('font-size', '24px'),
        ('text-align', 'center'),
        ('font-weight', 'bold'),
        ('color', 'blue'),
        ('background-color', 'lightgrey')
    ]

    # Set CSS properties for td elements in pandas DataFrame
    td_props = [
        ('font-size', '18px'),
        ('text-align', 'center'),
        ('color', 'white')
    ]

    # Set table styles
    styles = [
        dict(selector="th", props=th_props),
        dict(selector="td", props=td_props)
    ]

    return (df_bid.style
            .apply(color_position_lines, axis=1)
            .format({'Total Pay': "${:20,.0f}"})
            .set_table_styles(styles)
            )


def main():
    # Constant for column location of crew.
    CREW_COL = 3

    # Read in data from excel file to pandas DataFrame.
    df_lines = pd.read_excel('data/monthly_lines.xlsx')

    # Convert pandas DataFrame to a list.
    lines = df_lines.values.tolist()

    # List to hold Line objects.
    line_instances = []

    # Instantiate Line objects.
    for item in lines:
        if item[CREW_COL] > 1:
            line_instances.append(PurserLine(*item))
            line_instances.append(FALine(*item))
        else:
            line_instances.append(FALine(*item))

    # Sort Line objects from Greatest to Least (pay).
    sorted_lines = sorted(line_instances, reverse=True)

    # Create pandas DataFrame from sorted Line objects.
    df_bid = pd.DataFrame([obj.as_dict() for obj in sorted_lines])

    # Start data frame index at 1 instead of 0.
    df_bid.index = df_bid.index + 1

    # Apply formatting to DataFrame.
    styled_bid = style_df(df_bid)

    # Render DataFrame as HTML.
    html = styled_bid.render()

    # Write sorted and formatted DataFrame to HTML file.
    with open('monthly_bid.html', 'w') as fp:
        fp.write(html)

    # Create PDF from HTML file
    pdf.from_file('monthly_bid.html', 'monthly_bid.pdf')


if __name__ == "__main__":
    main()
