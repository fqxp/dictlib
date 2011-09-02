class ValidationError(Exception):
    """ Thrown when validation fails.
    """
    pass

class SchemaFieldNotFound(Exception):
    """ Thrown when trying to access a non-existing schema field.
    """
    pass

