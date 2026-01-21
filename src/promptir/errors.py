"""Custom exception types for promptir."""


class PromptError(Exception):
    """Base error for promptir."""


class PromptCompileError(PromptError):
    """Raised when compilation fails."""


class PromptNotFound(PromptError):
    """Raised when a prompt id/version is missing."""


class PromptInputError(PromptError):
    """Raised for invalid runtime inputs."""
