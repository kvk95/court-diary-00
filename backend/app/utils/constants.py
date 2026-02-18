# null value for MySql Year column
MIN_YEAR = 1900
MAX_YEAR = 9999

# the profile image URL
PROFILE_IMAGE_URL = "api/profile/{user_id}.png"

# Upload folder configuration
UPLOAD_FOLDER = "./uploads"

# Allowed extensions for file upload
IMAGE_ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
IMAGE_ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/gif"]


PAGINATION_DEFAULT_PAGE = 1
PAGINATION_DEFAULT_LIMIT = 10

SUPERADMIN_MODULE_CODE = "SUP"

MAX_RETRIES: int = 3

JINJA_TEMPLATES_PATH = "static"
