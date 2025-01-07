from pandas import DataFrame, Series, isna

def compare_first_characters(data: DataFrame, first_column_name: str, second_column_name: str, number_of_characters: int = 1) -> Series:
    """
    Checks whether the first 'number_of_characters 'values in `first_column_name` and `second_column_name` are similar, and if the values are None or NaN.

    If the characters are not equal, assigns a score of 0.
    If the characters are equal, assigns a score of 1.
    """

    def check(value):

        if isna(value[first_column_name]):
            return 0
        # END IF

        if isna(value[second_column_name]):
            return 0
        # END IF

        str_first_value = str(value[first_column_name])
        str_second_value = str(value[second_column_name])

        return 1 if str_first_value[:number_of_characters] == str_second_value[:number_of_characters] else 0
    # END check

    return data[[first_column_name, second_column_name]].apply(check, axis=1)
# END compare_first_characters
