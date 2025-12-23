import functools
import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Union

from pyflink.common import Types
from pyflink.datastream import DataStream


def _serialize_input_document(input_document: Any) -> str:
    """
    Safely serialize an input document to a string.
    
    Parameters
    ----------
    input_document : Any
        The input document to serialize
        
    Returns
    -------
    str
        Serialized representation of the input document
    """
    if input_document is None:
        return None
    
    try:
        if isinstance(input_document, str):
            return input_document
        else:
            try:
                return json.dumps(input_document, default=str)
            except (TypeError, ValueError):
                return str(input_document)
    except Exception:
        return str(input_document)


def _exception_to_dict(
    error: Exception,
    input_document: Any = None,
    function_name: str = None,
) -> Dict[str, Any]:
    """
    Convert an exception to a simple dictionary with all error information.
    
    This avoids passing Exception objects through Flink's serialization,
    which can cause pickle errors with certain exception types.
    
    Parameters
    ----------
    error : Exception
        The exception that occurred
    input_document : Any, optional
        The input document being processed
    function_name : str, optional
        The name of the function where error occurred
        
    Returns
    -------
    dict
        Dictionary containing error information
    """
    return {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "stack_trace": "".join(traceback.format_exception(
            type(error),
            error,
            error.__traceback__,
        )),
        "input_document": _serialize_input_document(input_document),
        "function_name": function_name,
        "is_error": True,  # Marker to identify error dicts
    }


def safe_map(func: Callable) -> Callable:
    """
    Decorator to wrap MapFunction.map() methods with comprehensive error handling.

    Catches any uncaught exceptions that occur during message processing and converts
    them to error dictionaries instead of passing Exception objects through Flink's
    serialization, preventing job crashes.

    Usage:
        class MyMapFunction(MapFunction):
            @safe_map
            def map(self, value):
                # ... processing logic ...
                return result

    Parameters
    ----------
    func : Callable
        The map function to wrap with error handling

    Returns
    -------
    Callable
        The wrapped function that returns Union[Result, Dict] (where Dict is error info)
    """
    @functools.wraps(func)
    def wrapper(self, value: Any) -> Union[Any, Dict[str, Any]]:
        try:
            result = func(self, value)
            
            # If the function returned an exception, convert it to a dict immediately
            if isinstance(result, Exception):
                function_name = f"{self.__class__.__name__}.{func.__name__}"
                input_doc = getattr(result, '_flink_input_document', value)
                return _exception_to_dict(result, input_doc, function_name)
            
            return result
            
        except Exception as e:
            logging.exception(
                "Uncaught exception in %s.%s while processing value: %s",
                self.__class__.__name__,
                func.__name__,
                value,
            )
            
            # Convert exception to dict immediately to avoid serialization issues
            function_name = f"{self.__class__.__name__}.{func.__name__}"
            return _exception_to_dict(e, value, function_name)
            
    return wrapper


def format_error_message(
    error: Union[Exception, Dict[str, Any]],
    job_name: str,
    input_document: Any = None,
) -> str:
    """
    Format an exception or error dict into a structured JSON error message for Kafka.

    Parameters
    ----------
    error : Exception | dict
        The exception that occurred or error dictionary from @safe_map
    job_name : str
        Name of the job/operation where the error occurred
    input_document : Any, optional
        The input document being processed when the error occurred

    Returns
    -------
    str
        JSON-formatted error message
    """
    # If it's already an error dict from @safe_map, use it directly
    if isinstance(error, dict) and error.get("is_error"):
        error_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "job_name": job_name,
            "function_name": error.get("function_name"),
            "error_type": error.get("error_type"),
            "error_message": error.get("error_message"),
            "stack_trace": error.get("stack_trace"),
            "input_document": error.get("input_document"),
        }
    else:
        # Fallback for regular exceptions (shouldn't happen with @safe_map)
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        function_name = getattr(error, '_flink_function_name', None)
        
        # Get input document
        if input_document is None and hasattr(error, '_flink_input_document'):
            input_document = getattr(error, '_flink_input_document')
        
        error_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "job_name": job_name,
            "function_name": function_name,
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "input_document": _serialize_input_document(input_document),
        }

    return json.dumps(error_data)


def extract_errors(data_stream: DataStream, job_name: str) -> DataStream:
    """
    Extract errors from a data stream and format them as JSON error messages.

    This function filters out error dictionaries (created by @safe_map) from the stream
    and converts them into structured error messages for the Kafka error topic.

    Parameters
    ----------
    data_stream : DataStream
        The data stream that may contain error dictionaries or lists containing errors
    job_name : str
        Name of the job/operation for error tracking

    Returns
    -------
    DataStream
        A stream of JSON-formatted error messages
    """
    def is_error(value):
        """Check if value is an error dict."""
        return isinstance(value, dict) and value.get("is_error") == True
    
    def extract(value):
        """Extract errors from value, handling both single values and lists."""
        # If it's a list, check each item
        if isinstance(value, list):
            return [format_error_message(item, job_name) for item in value if is_error(item)]
        # If it's a single error dict, return it
        elif is_error(value):
            return [format_error_message(value, job_name)]
        # Otherwise, no errors
        return []
    
    return data_stream.flat_map(extract, Types.STRING()).name(f"{job_name}_errors")


def filter_successful(data_stream: DataStream) -> DataStream:
    """
    Filter out errors from a data stream, keeping only successful results.

    Parameters
    ----------
    data_stream : DataStream
        The data stream that may contain both results and error dictionaries, or lists

    Returns
    -------
    DataStream
        A stream containing only successful results (non-error items), flattened
    """
    def is_error(value):
        """Check if value is an error dict."""
        return isinstance(value, dict) and value.get("is_error") == True
    
    def filter_errors(value):
        """Filter out errors from value, handling both single values and lists."""
        # If it's a list, filter out errors and return non-error items
        if isinstance(value, list):
            return [item for item in value if not is_error(item)]
        # If it's a single error dict, filter it out
        elif is_error(value):
            return []
        # Otherwise, it's a successful result
        return [value]
    
    return data_stream.flat_map(filter_errors).name("successful_results")
