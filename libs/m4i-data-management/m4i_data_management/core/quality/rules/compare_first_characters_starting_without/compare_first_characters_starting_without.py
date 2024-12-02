from pandas import DataFrame, Series
from ..compare_first_characters import compare_first_characters
from ..starts_with import starts_with


def compare_first_characters_starting_without(data: DataFrame, first_column_name: str, second_column_name: str,
                                              number_of_characters: int, *prefixes: str) -> Series:
  """
  Checks whether the first 'number_of_characters 'values in `first_column_name` and `second_column_name` are similar,
  and if  `column_name` does not start with any of the given `prefixes` , and if the values are None or NaN.

  If the characters are not equal or contain nan, assigns a score of 0.
  If the first_column character does start with prefix, or is nan, assign a score of 0
  If the characters are equal AND first_column character does not start with prefix, assigns a score of 1.
  """

  def check(value):
    return 1 if value["same_first_char"] == 1 and value['start_with'] == 0 else 0
  # END check

  same_first_char = compare_first_characters(data, first_column_name, second_column_name, number_of_characters)
  start_with = starts_with(data, first_column_name, *prefixes)

  return DataFrame({"same_first_char": same_first_char, "start_with": start_with}).apply(check, axis=1)
# END compare_first_characters_starting_without
