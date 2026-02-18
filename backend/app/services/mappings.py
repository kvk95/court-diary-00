from typing import Any, Dict

# ── PROFILE MAPPINGS ─────────────────────────────────────────────────────
USER_TABLE_FIELDS = {"first_name", "last_name", "phone", "email", "image"}

USER_PROFILE_EXTRA_FIELDS = {
    "address",
    "country",
    "state",
    "city",
    "postal_code",
    "header_color",
    "sidebar_color",
    "primary_color",
    "font_family",
}

USER_FIELD_MAP = {
    "first_name": "firstName",
    "last_name": "lastName",
    "phone": "phoneNumber",
    "email": "email",
    "image": "image",
}

PROFILE_FIELD_MAP = {
    "address": "address",
    "country": "country",
    "state": "state",
    "city": "city",
    "postal_code": "postalCode",
    "header_color": "headerColor",
    "sidebar_color": "sidebarColor",
    "primary_color": "primaryColor",
    "font_family": "fontFamily",
}

COMPANY_FIELD_MAP = {
    "company_name": "companyName",
    "company_email": "companyEmail",
    "phone_number": "phoneNumber",
    "fax": "fax",
    "website": "website",
    "address": "address",
    "country": "country",
    "state": "state",
    "city": "city",
    "postal_code": "postalCode",
    "company_icon": "companyIcon",
    "favicon": "favicon",
    "company_logo": "companyLogo",
    "company_dark_logo": "companyDarkLogo",
}

ROLE_FIELD_MAP = {
    "role_name": "roleName",
    "status": "status",
    "description": "description",
}

ROLE_PERMISSION_FIELD_MAP = {
    "module_id": "moduleId",
    "allow_all": "allowAll",
    "can_read": "canRead",
    "can_write": "canWrite",
    "can_create": "canCreate",
    "can_delete": "canDelete",
    "can_import": "canImport",
    "can_export": "canExport",
}

USER_FIELD_MAP = {
    "username": "username",
    "email": "email",
    "first_name": "firstName",
    "last_name": "lastName",
    "phone": "phone",
    "status": "status",
    "image": "image",
    "email_verified": "emailVerified",
    "phone_verified": "phoneVerified",
    "two_factor_enabled": "twoFactorEnabled",
    "google_auth_connected": "googleAuthConnected",
}


def map_payload(payload_dict: Dict[str, Any], allowed_keys: set) -> Dict[str, Any]:

    data = {k: v for k, v in payload_dict.items() if k in allowed_keys}
    return data


# ── HELPER: Safe field mapper ───────────────────────────────────────────
def map_fields(data: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    return {
        new_key: data.get(old_key)
        for new_key, old_key in mapping.items()
        if data.get(old_key) is not None
    }
