from pandas import DataFrame, Series, isna


def unallowed_text(data: DataFrame, column_name: str, text: str) -> Series:
    """
    Checks if values in the column with the given `column_name` contain a specific unallowed `text` (e.g. 'BG Van Oord'). 
    
    This only works for textual values.
    If a value is not a string, it is converted to a string before comparison.

    If the value does not contain the given `text`, or if the value is empty, assigns a score of 1. 
    Otherwise, assigns a score of 0.
    """

    def check(value):

        if isna(value):
            return 1
        # END IF

        return 1 if text not in str(value) else 0
    # END check

    return data[column_name].apply(check)
# END unallowed_text
