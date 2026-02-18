# create_constants_context.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, inspect

# Load environment variables
load_dotenv()
DB_ENGINE = os.getenv("DB_ENGINE")
if not DB_ENGINE:
    raise ValueError("DB_ENGINE environment variable is not set!")

engine = create_engine(DB_ENGINE)
metadata = MetaData()

# Output file – single React context file
OUTPUT_FILE = os.path.join(
    os.getcwd(), "..", "frontend", "src", "contexts", "ConstantsContext.tsx"
)
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# Columns to ignore (audit / system fields)
IGNORED_COLUMNS = {
    "id",
    "created_by",
    "created_date",
    "updated_by",
    "updated_date",
    "is_active",
    "sort_order",
}


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase: refm_coupon_types → refmCouponTypes"""
    parts = snake_str.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def get_ts_type(column_name: str, type_str: str) -> str:
    """
    Infer simple TypeScript type for refm table columns.
    - TINYINT (common for flags) → boolean
    - Columns ending with _ind → boolean
    - Columns ending with _id → string (foreign key reference)
    - Everything else → string
    """
    col_lower = column_name.lower()
    type_upper = type_str.upper()

    if "TINYINT" in type_upper or col_lower.endswith("_ind"):
        return "boolean"
    if col_lower.endswith("_id"):
        return "string"
    return "string"


def generate_constants_context():
    metadata.reflect(bind=engine)
    inspector = inspect(engine)

    # Only process tables starting with refm_
    refm_tables = [t for t in inspector.get_table_names() if t.startswith("refm_")]
    refm_tables.sort()  # consistent order

    print("⏳ Generating ConstantsContext.tsx...")
    if not refm_tables:
        print("❌ No refm_* tables found in the database.")
        return

    print(f"🔎 Found {len(refm_tables)} refm tables: {', '.join(refm_tables)}")

    # Collect lines for the two dynamic sections
    interface_lines = ["interface ConstantData {"]
    initial_lines = ["const initialConstants: ConstantData = {"]

    for table_name in refm_tables:
        table = Table(table_name, metadata, autoload_with=engine)

        # Filter out ignored columns
        relevant_columns = [
            col for col in table.columns if col.name not in IGNORED_COLUMNS
        ]

        if not relevant_columns:
            print(f"  → Skipping {table_name} (no relevant columns after filtering)")
            continue

        camel_key = to_camel_case(table_name)
        # tble_key = table_name.upper().removeprefix("REFM_")
        tble_key = table_name.upper()

        # Build object type: { code: string; description: string; country_id: string; ... }
        field_types = []
        for col in relevant_columns:
            ts_type = get_ts_type(col.name, str(col.type))
            field_types.append(f"{col.name}: {ts_type}")

        interface_lines.append(f"  {tble_key}: {{ {'; '.join(field_types)} }}[];")
        initial_lines.append(f"  {tble_key}: [],")

    interface_lines.append("}")
    initial_lines.append("};")

    # Full template (everything else stays exactly the same)
    template = """/// {OUTPUT_FILE}

import React, {{
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
}} from "react";
import {{ useAuth }} from "@/contexts/AuthContext";

// === AUTO-GENERATED SECTION START ===
// Define the structure of your constants data
{interface_block}

// Initial state (optional, for safety before data loads)
{initial_block}
// === AUTO-GENERATED SECTION END ===

interface ConstantsContextType extends ConstantData {{
  /** Get description by code from a specific refm list */
  getDescription: (
    list: keyof ConstantData,
    code: string
  ) => string | undefined;

  /** Get full item by code from a specific refm list */
  getItem: <T extends keyof ConstantData>(
    list: T,
    code: string
  ) => ConstantData[T][number] | undefined;
}}

const ConstantsContext = createContext<ConstantsContextType>({{
  ...initialConstants,
  getDescription: () => undefined,
  getItem: () => undefined,
}});

interface ConstantsProviderProps {{
  children: ReactNode;
}}

// B. The Provider Component (Loads data on App Start)
export const ConstantsProvider: React.FC<ConstantsProviderProps> = ({{
  children,
}}) => {{
  const [constants, setConstants] = useState<ConstantData>(initialConstants);
  const [isLoading, setIsLoading] = useState(true);
  const {{ loadRefm }} = useAuth();

  useEffect(() => {{
    // This effect runs only once after the component mounts (on server start)
    const fetchConstants = async () => {{
      try {{
        const response = await loadRefm();
        setConstants(response.result);
      }} catch (error) {{
        console.error("Failed to fetch application constants:", error);
        // Fallback to local or default values if API fails
        setConstants(initialConstants);
      }} finally {{
        setIsLoading(false);
      }}
    }};

    fetchConstants();
  }}, []); // Empty dependency array ensures it runs only once

  // Function to get the description based on code and refm entry type
  const getDescription = (list: keyof ConstantData, code: string) => {{
    const entry = constants[list].find((item) => item.code === code);
    return entry ? entry.description : code;
  }};

  // Helper: Get full item by code (generic)
  const getItem = <T extends keyof ConstantData>(
    list: T,
    code: string
  ): ConstantData[T][number] | undefined => {{
    const items = constants[list] as ConstantData[T];
    return items.find((item: any) => item.code === code);
  }};

  // Optional: Show a loading state for the whole application
  if (isLoading) {{
    return <div>Loading initial application data...</div>;
  }}

  return (
    <ConstantsContext.Provider
      value={{{{ ...constants, getDescription, getItem }}}}
    >
      {{children}}
    </ConstantsContext.Provider>
  );
}};

// C. The Hook to Consume the Constants
export const useRefmConstants = () => {{
  return useContext(ConstantsContext);
}};
"""

    full_code = template.format(
        OUTPUT_FILE=OUTPUT_FILE.split("..")[1].strip("/"),
        interface_block="\n".join(interface_lines),
        initial_block="\n".join(initial_lines),
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(full_code.rstrip() + "\n")

    print(f"✅ Successfully UI's ConstantsContext generated !!\n\t➥ {OUTPUT_FILE}\n\n")


if __name__ == "__main__":
    generate_constants_context()
