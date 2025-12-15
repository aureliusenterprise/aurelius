import functools
import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Any, Callable, Union

from pyflink.common import Types
from pyflink.datastream import DataStream


def safe_map(func: Callable) -> Callable:
    """
    Decorator to wrap MapFunction.map() methods with comprehensive error handling.

    Catches any uncaught exceptions that occur during message processing and returns
    them as Exception objects with the input document attached, preventing the Flink 
    job from crashing.

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
        The wrapped function that returns Union[Result, Exception]
    """
    @functools.wraps(func)
    def wrapper(self, value: Any) -> Union[Any, Exception]:
        try:
            result = func(self, value)
            if isinstance(result, Exception):
                if not hasattr(result, '_flink_input_document'):
                    result._flink_input_document = value  # type: ignore
                if not hasattr(result, '_flink_function_name'):
                    result._flink_function_name = f"{self.__class__.__name__}.{func.__name__}"  # type: ignore
            return result
        except Exception as e:
            logging.exception(
                "Uncaught exception in %s.%s while processing value: %s",
                self.__class__.__name__,
                func.__name__,
                value,
            )
            e._flink_input_document = value  # type: ignore
            e._flink_function_name = f"{self.__class__.__name__}.{func.__name__}"  # type: ignore

            return e
    return wrapper


def format_error_message(
    error: Exception,
    job_name: str,
    input_document: Any = None,
) -> str:
    """
    Format an exception into a structured JSON error message for Kafka.

    Parameters
    ----------
    error : Exception
        The exception that occurred
    job_name : str
        Name of the job/operation where the error occurred
    input_document : Any, optional
        The input document being processed when the error occurred

    Returns
    -------
    str
        JSON-formatted error message
    """
    if input_document is None and hasattr(error, '_flink_input_document'):
        input_document = getattr(error, '_flink_input_document')
    
    function_name = getattr(error, '_flink_function_name', None)
    
    input_doc_str = None
    if input_document is not None:
        try:
            if isinstance(input_document, str):
                input_doc_str = input_document
            else:
                try:
                    input_doc_str = json.dumps(input_document, default=str)
                except (TypeError, ValueError):
                    input_doc_str = str(input_document)
        except Exception:
            input_doc_str = str(input_document)
    
    error_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "job_name": job_name,
        "function_name": function_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "stack_trace": "".join(traceback.format_exception(type(error), error, error.__traceback__)),
        "input_document": input_doc_str,
    }

    return json.dumps(error_data)


def extract_errors(data_stream: DataStream, job_name: str) -> DataStream:
    """
    Extract errors from a data stream and format them as JSON error messages.

    This function filters out Exception objects from the stream and converts them
    into structured error messages that can be sent to a Kafka error topic.

    Parameters
    ----------
    data_stream : DataStream
        The data stream that may contain Exception objects
    job_name : str
        Name of the job/operation for error tracking

    Returns
    -------
    DataStream
        A stream of JSON-formatted error messages
    """
    return data_stream.flat_map(
        lambda value: [format_error_message(value, job_name)] if isinstance(value, Exception) else [],
        Types.STRING(),
    ).name(f"{job_name}_errors")


def filter_successful(data_stream: DataStream) -> DataStream:
    """
    Filter out errors from a data stream, keeping only successful results.

    Parameters
    ----------
    data_stream : DataStream
        The data stream that may contain both results and Exception objects

    Returns
    -------
    DataStream
        A stream containing only successful results (non-Exception objects)
    """
    return data_stream.flat_map(
        lambda value: [] if isinstance(value, Exception) else [value],
    ).name("successful_results")
