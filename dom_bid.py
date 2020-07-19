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
        pay_credit  (float): The hourly pay + purser pay + international (Central America) pay, for the line.
        per_diem    (float): The per diem pay for the line.
        pay_total   (float): The total pay value for the line (hourly + per diem).
    """

    PAY_RATE = 65.79 / 60.0         # Pay rate per minute
    FMP_RATE_DOM = 1.0 / 60.0       # Purser pay rate per minute - Domestic
    FMP_RATE_INT = 2.0 / 60.0       # Purser pay rate (per minute) - International (Central America)
    INTERNATIONAL_PAY = 2.0 / 60.0  # International pay rate (per minute)
    PER_DIEM_RATE = 2.25 / 60.0     # Per diem rate per minute
    MINIMUM = 71 * 60               # Monthly minimum guaranteed credit (in minutes)

    def __init__(self, line_number, credit, tafb, crew, international, position=None):
        """
        The constructor for the Line class.

        Parameters:
            line_number   (int):   The monthly bid line number.
            credit        (int):   The total credit hours for the line.
            tafb          (int):   The 'time away from base' for the line.
            crew          (int):   The number of crew positions for the line.
            international (bool):  Whether the line is an international (Central American) line.
            position      (str):   The position, FMP or FA, to bid for the line.
        """

        self.line_number = int(line_number)
        self.credit = int(self.__convert_minutes(credit))
        self.tafb = int(self.__convert_minutes(tafb))
        self.crew = int(crew)
        self.international = bool(international)
        self.position = position
        self.pay_credit = self.__calculate_pay()
        self.per_diem = self.__calculate_per_diem()
        self.pay_total = self.pay_credit + self.per_diem

    def __eq__(self, other):
        """
        Tests equality of pay for two Line objects.

        Parameter:
            other (Line): The other Line object to which self is being compared.

        Returns:
            (bool): Returns True if the pay for the two objects are equal.
        """

        return self.pay_total == other.pay_total

    def __lt__(self, other):
        """
        Tests whether the pay for object self is less than the pay for object other.

        Parameter:
            other (Line): The other Line object to which self is being compared.

        Returns:
            (bool): Returns True if the pay for object self is less than the pay for object other.
        """

        return self.pay_total < other.pay_total

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
        Calculates the line credit pay for the month.

        It calculates pay based in the following:
            - if credit hours < contractual minimum guaranteed hours,
                  minimum guaranteed hours is used
            - if credit hours >= contractual minimum guaranteed hours,
                  credit hours is used
            -- if line is an international (Central American) line, International pay is added to the pay for the line
            -- if position is FMP, Purser pay is added to the pay for the line

        Returns:
            (float): The line credit pay (hourly + purser pay [if applicable] + international pay [if applicable])
        """

        if self.credit < self.MINIMUM:
            pay = self.MINIMUM * self.PAY_RATE
        else:
            pay = self.credit * self.PAY_RATE

        if self.international and self.position == 'FMP':
            return pay + self.credit * (self.INTERNATIONAL_PAY + self.FMP_RATE_INT)
        elif self.international and self.position != 'FMP':
            return pay + self.credit * self.INTERNATIONAL_PAY
        elif self.position == 'FMP':
            return pay + self.credit * self.FMP_RATE_DOM
        else:
            return pay

    def __calculate_per_diem(self):
        """
        Calculates the per diem pay for the line.

        Returns:
             (float): The total per diem pay for the line
        """

        return self.tafb * self.PER_DIEM_RATE

    def as_dict(self):
        """
        Used to create a dictionary to be used by pandas DataFrame constructor.

        Is called to create output file of the data we are interested in.

        Returns:
            (Line): Dictionary containing line number, position, total pay, pay credit, and per diem

        Reference:
        https://stackoverflow.com/questions/47623014/converting-a-list-of-objects-to-a-pandas-dataframe
        """

        return {'Line Number': self.line_number, 'Position': self.position, 'Total Pay': self.pay_total,
                'Pay Credit': self.pay_credit, 'Per Diem': self.per_diem}


class PurserLine(Line):
    """
    This is a class for Purser bid lines.

    It is a child of class Line that sets the position attribute to FMP.
    """

    def __init__(self, line_number, credit, tafb, crew, international):
        Line.__init__(self, line_number, credit, tafb, crew, international, position='FMP')


class FALine(Line):
    """
    This is a class for Flight Attendant bid lines.

    It is a child of class Line that sets the position attribute to Any FA.
    """

    def __init__(self, line_number, credit, tafb, crew, international):
        Line.__init__(self, line_number, credit, tafb, crew, international, position='Any FA')


def color_position_lines(d):
    """
    Function that sets the color of the line based on position type (FMP or Any FA).

    It colors the line orange if it is a purser line and blue if it is a flight
    attendant line.

    Reference:
        https://kanoki.org/2019/01/02/pandas-trick-for-the-day-color-code-columns-rows-cells-of-dataframe/
    """

    if d.Position == 'FMP':
        return ['background-color: orange'] * 5
    else:
        return ['background-color: blue'] * 5


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
            .format({'Total Pay': "${:20,.0f}", 'Pay Credit': "${:20,.0f}", 'Per Diem': "${:20,.0f}"})
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

    # Get first 150 rows of sorted Line objects
    df_bid_150 = df_bid.head(150)

    # Apply formatting to DataFrame.
    styled_bid = style_df(df_bid_150)

    # Render DataFrame as HTML.
    html = styled_bid.render()

    # Write sorted and formatted DataFrame to HTML file.
    with open('monthly_bid.html', 'w') as fp:
        fp.write(html)

    # Create PDF from HTML file
    pdf.from_file('monthly_bid.html', 'monthly_bid.pdf')


if __name__ == "__main__":
    main()
