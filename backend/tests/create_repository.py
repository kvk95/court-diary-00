# create_repository.py
import os

# === DIRECTORIES (same style as your create_model.py) ===
# Directory where models are saved
MODEL_OUTPUT_DIR = os.path.join(os.getcwd(), "app", "database", "models")

# Directory where repository files will be saved
REPOSITORY_OUTPUT_DIR = os.path.join(os.getcwd(), "app", "database", "repositories")

# Ensure the repositories folder exists (same pattern as your model script)
if not os.path.exists(REPOSITORY_OUTPUT_DIR):
    os.makedirs(REPOSITORY_OUTPUT_DIR)

# Repository template (exactly matching your skeleton)
REPOSITORY_TEMPLATE = """from typing import List, Optional, Tuple, Dict

from sqlalchemy import select, func, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base.repo_context import apply_repo_context
from app.database.repositories.base.base_repository import BaseRepository
from app.database.models.{module_name} import {class_name}

@apply_repo_context
class {class_name}Repository(BaseRepository[{class_name}]):
    def __init__(self):
        super().__init__({class_name})
"""


def generate_class_name(table_name: str) -> str:
    """Convert snake_case table name to PascalCase class name"""
    return "".join(word.capitalize() for word in table_name.split("_"))


def get_existing_model_files():
    """Return list of .py files in models directory (excluding base files)"""
    if not os.path.exists(MODEL_OUTPUT_DIR):
        print(f"Model directory not found: {MODEL_OUTPUT_DIR}")
        print("Run create_model.py first!")
        return []

    model_files = []
    for filename in os.listdir(MODEL_OUTPUT_DIR):
        if filename.endswith(".py") and filename not in {
            "base_model.py",
            "__init__.py",
            "timestampmixin.py",
            "base.py",  # in case you have other base files
        }:
            model_files.append(filename)
    return model_files


def generate_repository_file(model_filename: str):
    """Generate a single repository file from a model file"""
    table_name = model_filename[:-3]  # remove .py

    if table_name.startswith("refm"):
        print(
            f"⚠️  Skipping repository generation for '{model_filename}' (starts with 'refm')."
        )
        return

    class_name = generate_class_name(table_name)
    module_name = table_name  # same as filename without .py

    repo_filename = f"{table_name}_repository.py"
    repo_filepath = os.path.join(REPOSITORY_OUTPUT_DIR, repo_filename)

    # Skip if repository already exists
    if os.path.exists(repo_filepath):
        print(f"↻ Repository already exists → skipping: {repo_filename}")
        return

    # Generate content
    content = REPOSITORY_TEMPLATE.format(module_name=module_name, class_name=class_name)

    # Write file
    with open(repo_filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

    print(f"🆗 Generated → {repo_filename}")


def generate_repositories():
    """Main function: generate all missing repository files"""
    print("⏳ Starting repository generation...")

    model_files = get_existing_model_files()

    if not model_files:
        print("❌ No model files found. Make sure to run create_model.py first!")
        return

    for model_file in model_files:
        generate_repository_file(model_file)

    print("✅ All repositories generated successfully!\n\n")


if __name__ == "__main__":
    generate_repositories()
