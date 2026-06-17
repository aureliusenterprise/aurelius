import json

from pandas import DataFrame


class BaseModel:
    """
    This class is intended to be inherited by all model objects.
    Classes inheriting BaseModel can be easily (de)serialized
    from/to JSON.

    Inheriting classes can define their attributes as a list of
    tuples (attr_name, attr_type, is_list):

    .. code-block:: python

        class ExampleModel(BaseModel):
           _fields = [
               ('simple_attr', str, False)
               , ('complex_attr', Class, False)
               , ('int_array', int, True) # The boolean signifies
                 # that this is an array
               , ...
           ]
        # END ExampleModel

    `Source <http://www.seanjohnsen.com/2016/11/23/
        pydeserialization.html>`_

    The BaseModel constructor takes an arbitrary number of
    key-value pairs. Parameters for which the key does not
    occur in the _fields definition of the class are ignored.
    Specified _fields that do not exist in the parameters are
    assigned the None value.
    """

    _fields = []

    def _init_arg(self, expected_type, value, is_list=False):
        # First, check whether we are dealing with a list
        if value is not None:
            if is_list:
                return list(map(lambda i: self._init_arg(expected_type, i), value))
            elif isinstance(value, list):
                return self._init_arg(expected_type, value, True)

        # Else, if we are dealing with a single value, map it to the correct type
        if value is None or isinstance(value, expected_type):
            return value
        elif issubclass(expected_type, BaseModel) and isinstance(value, dict):
            return expected_type(**value)
        else:
            return expected_type(value)  # type: ignore[reportGeneralTypeIssues]

    # END _init_arg

    def __init__(self, **kwargs):
        """
        Initialize this instance from a dict of keyword arguments.

        :param dict kwargs: The property values for this instance
        """
        field_names, field_types, are_list = zip(*self._fields)

        assert [isinstance(name, str) for name in field_names]
        assert [isinstance(type_, type) for type_ in field_types]
        assert [isinstance(bool_, bool) for bool_ in are_list]

        for name, field_type, is_list in self._fields:
            setattr(self, name, self._init_arg(field_type, kwargs.get(name), is_list))
        # END LOOP

    # END __init__

    def toJSON(self):
        """
        Serialize this instance as a JSON string

        :returns: A JSON string representing this object
        :rtype: str
        """
        return json.dumps(self.toDict())

    # END toJSON

    @classmethod
    def fromJSON(cls, data):
        """
        Deserialize a new instance of this class from a JSON string

        :returns: An instance of the class on which this method was called,
            with the given attribute values.
        :rtype: BaseModel

        :param str data: A JSON string describing the instance

        :exception TypeError: Thrown when the JSON string contained
            invalid arguments
        :exception ValueError: Thrown when the given string could not
            be parsed as JSON
        """

        return cls.fromDict(json.loads(data))

    # END fromJSON

    def toDataFrame(self):
        """
        Transform this instance to a Pandas DataFrame

        :returns: A Pandas DataFrame mirroring this instance
        :rtype: DataFrame
        """

        return DataFrame(self.toDict())

    # END toDataFrame

    @classmethod
    def fromDataFrame(cls, df):
        """
        Map a Pandas DataFrame to instances of this class

        :returns: A list of instances of this class for each row
            in the dataframe
        :rtype: array<BaseModel>

        :param DataFrame df: The Pandas DataFrame containing the
            records you wish to map to this class
        """

        return df.to_dict(into=cls)

    # END fromDataFrame

    def toDict(self):
        """
        Transform this instance into regular python dict containing
        all properties of this object.

        :returns: A python dict containing all properties of this object.
        :rtype: dict
        """

        return vars(self)

    # END toDict

    @classmethod
    def fromDict(cls, dict):
        """
        Create a new instance of this class based on the given dict

        :returns: A new instance of this class based on the given dict
        :rtype: BaseModel

        :param dict dict: The dict providing the property values
        """

        return cls(**dict)

    # END fromDict


# END BaseModel
