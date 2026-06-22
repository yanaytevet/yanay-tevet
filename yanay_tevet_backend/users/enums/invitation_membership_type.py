from common.base_enum import BaseEnum


class InvitationMembershipType(BaseEnum):
    """Which per-app membership model an invitation should create on acceptance.

    Keyed by the membership model, not the app — Apartment Hunt and Villa
    Villekulla both use the same ``apartment_hunt.ProjectMembership``.
    """

    RENTAL_PROJECT = 'rental_project'
    TASK_PROJECT = 'task_project'
    ITINERARY_LIST = 'itinerary_list'
