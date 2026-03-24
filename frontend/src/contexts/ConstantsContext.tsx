/// \frontend\src\contexts\ConstantsContext.tsx

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useAuth } from "@/contexts/AuthContext";

// === AUTO-GENERATED SECTION START ===
// Define the structure of your constants data
interface ConstantData {
  REFM_AOR_STATUS: { code: string; description: string; color_code: string; status_ind: boolean }[];
  REFM_BILLING_STATUS: { code: string; description: string; color_code: string; status_ind: boolean }[];
  REFM_CASE_STATUS: { code: string; description: string; color_code: string; status_ind: boolean }[];
  REFM_CASE_TYPES: { code: string; description: string; status_ind: boolean }[];
  REFM_COLLAB_ACCESS: { code: string; description: string; permissions: string; color_code: string; status_ind: boolean }[];
  REFM_COMM_STATUS: { code: string; description: string; color_code: string; status_ind: boolean }[];
  REFM_COUNTRIES: { code: string; description: string; phone_code: string; status_ind: boolean }[];
  REFM_COURTS: { court_id: string; court_name: string; state_code: string; court_type: string; address: string; status_ind: boolean }[];
  REFM_EMAIL_ENCRYPTION: { code: string; description: string; status_ind: boolean }[];
  REFM_EMAIL_STATUS: { code: string; description: string; color_code: string }[];
  REFM_EMAIL_TEMPLATES: { code: string; subject: string; content: string; category: string; description: string; status_ind: boolean }[];
  REFM_HEARING_STATUS: { code: string; description: string; color_code: string; status_ind: boolean }[];
  REFM_INVITATION_STATUS: { code: string; description: string; color_code: string; status_ind: boolean }[];
  REFM_LOGIN_STATUS: { code: string; description: string }[];
  REFM_MODULES: { code: string; name: string; description: string; status_ind: boolean }[];
  REFM_PARTY_ROLES: { code: string; description: string; category: string; status_ind: boolean }[];
  REFM_PLAN_TYPES: { code: string; description: string; max_users: string; max_cases: string; price_monthly_amt: string; price_annual_amt: string; currency_code: string; status_ind: boolean }[];
  REFM_STATES: { code: string; description: string; country_code: string; status_ind: boolean }[];
  REFM_USER_DELETION_STATUS: { code: string; description: string; color_code: string; status_ind: boolean }[];
}

// Initial state (optional, for safety before data loads)
const initialConstants: ConstantData = {
  REFM_AOR_STATUS: [],
  REFM_BILLING_STATUS: [],
  REFM_CASE_STATUS: [],
  REFM_CASE_TYPES: [],
  REFM_COLLAB_ACCESS: [],
  REFM_COMM_STATUS: [],
  REFM_COUNTRIES: [],
  REFM_COURTS: [],
  REFM_EMAIL_ENCRYPTION: [],
  REFM_EMAIL_STATUS: [],
  REFM_EMAIL_TEMPLATES: [],
  REFM_HEARING_STATUS: [],
  REFM_INVITATION_STATUS: [],
  REFM_LOGIN_STATUS: [],
  REFM_MODULES: [],
  REFM_PARTY_ROLES: [],
  REFM_PLAN_TYPES: [],
  REFM_STATES: [],
  REFM_USER_DELETION_STATUS: [],
};
// === AUTO-GENERATED SECTION END ===

interface ConstantsContextType extends ConstantData {
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
}

const ConstantsContext = createContext<ConstantsContextType>({
  ...initialConstants,
  getDescription: () => undefined,
  getItem: () => undefined,
});

interface ConstantsProviderProps {
  children: ReactNode;
}

// B. The Provider Component (Loads data on App Start)
export const ConstantsProvider: React.FC<ConstantsProviderProps> = ({
  children,
}) => {
  const [constants, setConstants] = useState<ConstantData>(initialConstants);
  const [isLoading, setIsLoading] = useState(true);
  const { loadRefm } = useAuth();

  useEffect(() => {
    // This effect runs only once after the component mounts (on server start)
    const fetchConstants = async () => {
      try {
        const response = await loadRefm();
        setConstants(response.result);
      } catch (error) {
        console.error("Failed to fetch application constants:", error);
        // Fallback to local or default values if API fails
        setConstants(initialConstants);
      } finally {
        setIsLoading(false);
      }
    };

    fetchConstants();
  }, []); // Empty dependency array ensures it runs only once

  // Function to get the description based on code and refm entry type
  const getDescription = (list: keyof ConstantData, code: string) => {
    const entry = constants[list].find((item) => item.code === code);
    return entry ? entry.description : code;
  };

  // Helper: Get full item by code (generic)
  const getItem = <T extends keyof ConstantData>(
    list: T,
    code: string
  ): ConstantData[T][number] | undefined => {
    const items = constants[list] as ConstantData[T];
    return items.find((item: any) => item.code === code);
  };

  // Optional: Show a loading state for the whole application
  if (isLoading) {
    return <div>Loading initial application data...</div>;
  }

  return (
    <ConstantsContext.Provider
      value={{ ...constants, getDescription, getItem }}
    >
      {children}
    </ConstantsContext.Provider>
  );
};

// C. The Hook to Consume the Constants
export const useRefmConstants = () => {
  return useContext(ConstantsContext);
};
