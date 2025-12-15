"""Mock data services for CRM and credit scoring"""
from typing import Optional, Dict
import hashlib


# Mock CRM Database
CRM_DATABASE = {
    "CUST001": {
        "name": "Rajesh Kumar",
        "pan": "ABCDE1234F",
        "employment_type": "SALARIED",
        "monthly_income": 75000,
        "company": "Tech Corp India"
    },
    "CUST002": {
        "name": "Priya Sharma",
        "pan": "FGHIJ5678K",
        "employment_type": "SALARIED",
        "monthly_income": 95000,
        "company": "Finance Solutions Ltd"
    },
    "CUST003": {
        "name": "Amit Patel",
        "pan": "KLMNO9012P",
        "employment_type": "SELF_EMPLOYED",
        "monthly_income": 120000,
        "business": "Consulting Services"
    },
    "CUST004": {
        "name": "Sneha Reddy",
        "pan": "QRSTU3456V",
        "employment_type": "SALARIED",
        "monthly_income": 55000,
        "company": "Manufacturing Inc"
    },
    "CUST005": {
        "name": "Vikram Singh",
        "pan": "WXYZ7890A",
        "employment_type": "BUSINESS",
        "monthly_income": 150000,
        "business": "Retail Chain"
    },
    "CUST006": {
        "name": "Anita Desai",
        "pan": "BCDEF2345G",
        "employment_type": "SALARIED",
        "monthly_income": 45000,
        "company": "Healthcare Services"
    },
    "CUST007": {
        "name": "Karan Mehta",
        "pan": "GHIJK6789L",
        "employment_type": "SALARIED",
        "monthly_income": 85000,
        "company": "IT Solutions"
    },
    "CUST008": {
        "name": "Deepa Iyer",
        "pan": "MNOPQ0123R",
        "employment_type": "SELF_EMPLOYED",
        "monthly_income": 65000,
        "business": "Design Studio"
    },
    "CUST009": {
        "name": "Rahul Gupta",
        "pan": "STUVW4567X",
        "employment_type": "SALARIED",
        "monthly_income": 110000,
        "company": "Banking Sector"
    },
    "CUST010": {
        "name": "Meera Nair",
        "pan": "YZABC8901D",
        "employment_type": "SALARIED",
        "monthly_income": 20000,
        "company": "Small Enterprise"
    }
}


class MockCRMService:
    """Mock CRM service for customer data lookup"""
    
    @staticmethod
    def lookup_by_pan(pan: str) -> Optional[Dict]:
        """Lookup customer by PAN number"""
        for customer_id, data in CRM_DATABASE.items():
            if data["pan"] == pan.upper():
                return {
                    "customer_id": customer_id,
                    **data
                }
        return None
    
    @staticmethod
    def lookup_by_id(customer_id: str) -> Optional[Dict]:
        """Lookup customer by ID"""
        if customer_id in CRM_DATABASE:
            return {
                "customer_id": customer_id,
                **CRM_DATABASE[customer_id]
            }
        return None
    
    @staticmethod
    def verify_customer(name: str, pan: str, employment_type: str) -> tuple[bool, Optional[str], Optional[Dict]]:
        """
        Verify customer details
        
        Returns:
            (is_valid, customer_id, customer_data)
        """
        customer = MockCRMService.lookup_by_pan(pan)
        
        if not customer:
            return False, None, None
        
        # Check name match (case-insensitive, partial match allowed)
        name_match = name.lower() in customer["name"].lower() or customer["name"].lower() in name.lower()
        
        # Check employment type match
        employment_match = customer["employment_type"] == employment_type.upper()
        
        if name_match and employment_match:
            return True, customer["customer_id"], customer
        
        return False, customer["customer_id"], customer


class MockCreditScoreAPI:
    """Mock credit score API with deterministic scoring"""
    
    @staticmethod
    def get_credit_score(customer_id: str) -> int:
        """
        Get credit score for a customer (deterministic based on customer_id hash)
        
        Returns:
            Credit score between 600 and 850
        """
        # Use hash for deterministic but varied scores
        hash_value = int(hashlib.md5(customer_id.encode()).hexdigest(), 16)
        
        # Map to credit score range (600-850)
        score = 600 + (hash_value % 251)
        
        return score
    
    @staticmethod
    def get_credit_report(customer_id: str) -> Dict:
        """Get detailed credit report"""
        score = MockCreditScoreAPI.get_credit_score(customer_id)
        
        # Derive other metrics from score
        return {
            "credit_score": score,
            "score_range": "600-850",
            "credit_utilization": min(85, max(15, 100 - (score - 600) // 3)),
            "payment_history": "Good" if score >= 700 else "Fair" if score >= 650 else "Poor",
            "total_accounts": 3 + (hash_value % 8),
            "delinquencies": 0 if score >= 750 else 1 if score >= 650 else 2
        }
