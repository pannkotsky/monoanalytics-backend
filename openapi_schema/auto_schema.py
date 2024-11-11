from drf_standardized_errors.openapi import AutoSchema as DrfAutoSchema
from drf_standardized_errors.openapi_utils import InputDataField

from .util import to_camelcase


class AutoSchema(DrfAutoSchema):
    """Apply camel case for serializer field names in AutoSchema generated docs"""

    def _get_validation_error_codes_by_field(
        self, data_fields: list[InputDataField]
    ) -> dict[str, set[str]]:
        error_codes_by_field = super()._get_validation_error_codes_by_field(data_fields)
        return {
            to_camelcase(field): error_codes_by_field[field]
            for field in error_codes_by_field
        }
