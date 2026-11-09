class AIAddonException(Exception):
    """Base exception for add-on errors."""
    pass

class MissingAPIKeyError(AIAddonException):
    """Raised when API key is missing or empty."""
    pass

class InvalidServiceTier(AIAddonException):
    """Raised on 400 - Invalid service_tier argument"""
    pass

class InvalidAPIKeyError(AIAddonException):
    """
    Raised on 401 errors:
        401 - Invalid Authentication
        401 - Incorrect API key provided
        401 - You must be a member of an organization to use the API
        401 - IP not authorized
    """
    pass

class NotSupportedTerritoryError(AIAddonException):
    """Raised on 403 - Country, region, or territory not supported"""
    pass

class InvalidRequestError(AIAddonException):
    """Raised on 404 - Invalid request parameters."""
    pass

class QuotaError(AIAddonException):
    """
    Raised on 429 errors (out of credits):
        429 - Credit balance exhausted
        429 - Organization spend limit reached
        429 - Project spend limit reached
        429 - Organization usage limit reached
    """
    pass

class RateLimitError(AIAddonException):
    """
    Raised on 429 errors (rate limits):
        429 - Rate limit reached for requests
        429 - Slow down"""
    pass

class ServerUnavailableError(AIAddonException):
    """Raised on 5xx errors or connection timeouts."""
    pass

class ResponseTruncatedError(AIAddonException):
    """Raised when the output hits max tokens."""
    pass

class InvalidResponseFormatError(AIAddonException):
    """Raised when JSON parsing or schema validation fails."""
    pass