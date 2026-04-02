from app.database.models.case_clients import CaseClients
from app.database.models.case_aors import CaseAors
from app.database.models.user_chamber_link import UserChamberLink

RELATIONSHIP_CONFIG = {
    CaseClients: {
        "parent_field": "case_id",
        "child_field": "client_id",
        "entity": "CASE_CLIENT",
    },
    CaseAors: {
        "parent_field": "case_id",
        "child_field": "user_id",
        "entity": "CASE_AOR",
    },
    UserChamberLink: {
        "parent_field": "chamber_id",
        "child_field": "user_id",
        "entity": "USER_CHAMBER",
    },
}