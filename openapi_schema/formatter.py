from drf_standardized_errors.formatter import (
    ExceptionFormatter as DrfExceptionFormatter,
)
from drf_standardized_errors.types import ErrorResponse, ErrorType

from .util import to_camelcase


class ExceptionFormatter(DrfExceptionFormatter):
    def format_error_response(self, error_response: ErrorResponse):
        response = super().format_error_response(error_response)
        if error_response.type == ErrorType.VALIDATION_ERROR:
            errors = []
            for e in response["errors"]:
                error = {**e, "attr": to_camelcase(e["attr"])}
                errors.append(error)
            response["errors"] = errors

        return response
