"""
Database models matching desktop app structure
Adapted for PostgreSQL with full feature parity
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base
import enum


class UserRole(enum.Enum):
    ADMIN = "admin"
    SALES = "sales"
    PURCHASES = "purchases"
    PAYMENTS = "payments"
    RECEIPTS = "receipts"
    REPORTS = "reports"
    SETTINGS = "settings"


class AccountType(enum.Enum):
    CASH_BANK = "cash_bank"
    PARTY = "party"
    INCOME = "income"
    EXPENSE = "expense"
    TAX_LIABILITY = "tax_liability"
    CAPITAL = "capital"
    STOCK = "stock"


class VoucherType(enum.Enum):
    SALES = "sales"
    PURCHASE = "purchase"
    SALES_RETURN = "sales_return"
    PURCHASE_RETURN = "purchase_return"
    QUOTATION = "quotation"
    PURCHASE_ORDER = "purchase_order"
    CASH_RECEIPT = "cash_receipt"
    CASH_PAYMENT = "cash_payment"
    BANK_RECEIPT = "bank_receipt"
    BANK_PAYMENT = "bank_payment"
    JOURNAL = "journal"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    OPENING_BALANCE = "opening_balance"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ADMIN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company = relationship("Company", back_populates="users")


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(50))
    email = Column(String(255))
    address = Column(Text)
    gstin = Column(String(50))
    financial_year_start = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    users = relationship("User", back_populates="company")
    accounts = relationship("Account", back_populates="company")
    parties = relationship("Party", back_populates="company")
    products = relationship("Product", back_populates="company")
    vouchers = relationship("Voucher", back_populates="company")
    ledger_entries = relationship("LedgerEntry", back_populates="company")
    stock_movements = relationship("StockMovement", back_populates="company")


class Account(Base):
    __tablename__ = "ledger_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    account_name = Column(String(255), nullable=False, index=True)
    account_code = Column(String(50))
    account_type = Column(Enum(AccountType), nullable=False)
    group_name = Column(String(255))
    opening_balance = Column(Float, default=0.0)
    opening_balance_type = Column(String(10), default="Dr")
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company = relationship("Company", back_populates="accounts")
    debit_entries = relationship("LedgerEntry", foreign_keys="LedgerEntry.debit_account_id")
    credit_entries = relationship("LedgerEntry", foreign_keys="LedgerEntry.credit_account_id")


class Party(Base):
    __tablename__ = "parties"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    phone = Column(String(50))
    email = Column(String(255))
    address = Column(Text)
    gstin = Column(String(50))
    party_type = Column(String(20))  # debtor, creditor
    opening_balance = Column(Float, default=0.0)
    credit_limit = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company = relationship("Company", back_populates="parties")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True)
    category = Column(String(100))
    unit = Column(String(50))
    purchase_price = Column(Float, default=0.0)
    sale_price = Column(Float, default=0.0)
    gst_rate = Column(Float, default=0.0)
    cess_rate = Column(Float, default=0.0)
    hsn_code = Column(String(50))
    stock_quantity = Column(Float, default=0.0)
    minimum_stock = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company = relationship("Company", back_populates="products")
    stock_movements = relationship("StockMovement", back_populates="product")


class Voucher(Base):
    __tablename__ = "vouchers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    voucher_type = Column(Enum(VoucherType), nullable=False, index=True)
    voucher_no = Column(String(50), nullable=False, index=True)
    voucher_date = Column(String(50), nullable=False)
    party_id = Column(Integer, ForeignKey("parties.id"), nullable=True)
    party_name = Column(String(255))
    total_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    cess_amount = Column(Float, default=0.0)
    round_off = Column(Float, default=0.0)
    net_amount = Column(Float, default=0.0)
    payment_mode = Column(String(50))  # cash, credit, bank
    narration = Column(Text)
    is_posted = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company = relationship("Company", back_populates="vouchers")
    party = relationship("Party")
    items = relationship("VoucherItem", back_populates="voucher")
    ledger_entries = relationship("LedgerEntry", back_populates="voucher")


class VoucherItem(Base):
    __tablename__ = "voucher_items"
    
    id = Column(Integer, primary_key=True, index=True)
    voucher_id = Column(Integer, ForeignKey("vouchers.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(255))
    quantity = Column(Float, default=0.0)
    unit = Column(String(50))
    rate = Column(Float, default=0.0)
    amount = Column(Float, default=0.0)
    discount_percent = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    gst_rate = Column(Float, default=0.0)
    cess_rate = Column(Float, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    cess_amount = Column(Float, default=0.0)
    net_amount = Column(Float, default=0.0)
    
    voucher = relationship("Voucher", back_populates="items")
    product = relationship("Product")


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    voucher_id = Column(Integer, ForeignKey("vouchers.id"), nullable=True, index=True)
    voucher_type = Column(String(50), nullable=False, index=True)
    voucher_no = Column(String(50))
    voucher_date = Column(String(50), nullable=False, index=True)
    debit_account_id = Column(Integer, ForeignKey("ledger_accounts.id"), nullable=True)
    credit_account_id = Column(Integer, ForeignKey("ledger_accounts.id"), nullable=True)
    debit_amount = Column(Float, default=0.0)
    credit_amount = Column(Float, default=0.0)
    narration = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="ledger_entries")
    voucher = relationship("Voucher", back_populates="ledger_entries")
    debit_account = relationship("Account", foreign_keys=[debit_account_id])
    credit_account = relationship("Account", foreign_keys=[credit_account_id])


class StockMovement(Base):
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    voucher_id = Column(Integer, ForeignKey("vouchers.id"), nullable=True)
    movement_type = Column(String(50))  # in, out, adjustment
    quantity = Column(Float, default=0.0)
    rate = Column(Float, default=0.0)
    reference_type = Column(String(50))
    reference_no = Column(String(50))
    movement_date = Column(String(50))
    narration = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="stock_movements")
    product = relationship("Product", back_populates="stock_movements")
    voucher = relationship("Voucher")


class BankAccount(Base):
    __tablename__ = "bank_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    bank_name = Column(String(255))
    account_number = Column(String(50))
    account_type = Column(String(50))
    ifsc_code = Column(String(50))
    branch_name = Column(String(255))
    opening_balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    setting_key = Column(String(255), nullable=False, index=True)
    setting_value = Column(Text)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String(20))
    reference_type = Column(String(100))
    reference_id = Column(Integer)
    old_value = Column(Text)
    new_value = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
