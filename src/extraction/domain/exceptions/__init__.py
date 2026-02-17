"""Domain exceptions for extraction bounded context"""


class DomainError(Exception):
    """Base exception for domain rule violations."""
    pass


class CampaignError(DomainError):
    """Exception for campaign-related domain rule violations."""
    pass


class TaskError(DomainError):
    """Exception for task-related domain rule violations."""
    pass


class BotError(DomainError):
    """Exception for bot-related domain rule violations."""
    pass
