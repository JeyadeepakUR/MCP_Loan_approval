"""
Simple database integration for storing new customers
Run this to set up the database for production use
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Customer(Base):
    """Customer model for database storage"""
    __tablename__ = 'customers'
    
    customer_id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    pan = Column(String(10), unique=True, nullable=False)
    employment_type = Column(String(20), nullable=False)
    monthly_income = Column(Float, nullable=False)
    phone = Column(String(15))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///customers.db')

# Create engine
engine = create_engine(DATABASE_URL)

# Create tables
Base.metadata.create_all(engine)

# Create session factory
SessionLocal = sessionmaker(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_customer(name, pan, employment_type, monthly_income, phone=None, email=None):
    """Add a new customer to the database"""
    db = SessionLocal()
    
    try:
        # Generate customer ID
        count = db.query(Customer).count()
        customer_id = f"CUST{count + 1:03d}"
        
        customer = Customer(
            customer_id=customer_id,
            name=name,
            pan=pan.upper(),
            employment_type=employment_type.upper(),
            monthly_income=monthly_income,
            phone=phone,
            email=email
        )
        
        db.add(customer)
        db.commit()
        db.refresh(customer)
        
        print(f"✓ Customer added: {customer_id} - {name}")
        return customer
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error adding customer: {e}")
        return None
    finally:
        db.close()


def get_customer_by_pan(pan):
    """Retrieve customer by PAN"""
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.pan == pan.upper()).first()
        return customer
    finally:
        db.close()


def migrate_mock_data():
    """Migrate mock CRM data to database"""
    from services.mock_data import CRM_DATABASE
    
    db = SessionLocal()
    
    for customer_id, data in CRM_DATABASE.items():
        existing = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        
        if not existing:
            customer = Customer(
                customer_id=customer_id,
                name=data['name'],
                pan=data['pan'],
                employment_type=data['employment_type'],
                monthly_income=data['monthly_income']
            )
            db.add(customer)
            print(f"✓ Migrated: {customer_id} - {data['name']}")
    
    db.commit()
    db.close()
    print("\n✓ Migration complete!")


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE SETUP")
    print("=" * 60)
    
    print("\n1. Creating database tables...")
    Base.metadata.create_all(engine)
    print("✓ Tables created")
    
    print("\n2. Migrating mock data...")
    migrate_mock_data()
    
    print("\n3. Testing database...")
    test_customer = get_customer_by_pan("ABCDE1234F")
    if test_customer:
        print(f"✓ Test successful: Found {test_customer.name}")
    
    print("\n" + "=" * 60)
    print("Database ready for production!")
    print("=" * 60)
    print("\nTo add new customers:")
    print("  from setup_database import add_customer")
    print("  add_customer('Name', 'PAN', 'SALARIED', 75000)")
