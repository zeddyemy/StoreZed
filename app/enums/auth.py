from enum import Enum


class RoleNames(Enum):
    """ENUMS for the name filed in Role Model"""
    SUPER_ADMIN = "Super Admin"
    ADMIN = "Admin"
    JUNIOR_ADMIN = "Junior Admin"
    MODERATOR = "Moderator"
    CUSTOMER = "Customer"
    
    @classmethod
    def get_member_by_value(cls, value):
        return next((member for name, member in cls.__members__.items() if member.value == value), None)