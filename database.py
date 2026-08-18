from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey
)

from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    relationship
)


DATABASE_URL = "sqlite:///price_monitor.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


Session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# dashboard_v2 호환

SessionLocal = Session


Base = declarative_base()



# =========================
# Product
# =========================

class Product(Base):

    __tablename__ = "products"


    id = Column(
        Integer,
        primary_key=True
    )


    channel = Column(
        String
    )


    product = Column(
        String
    )


    url = Column(
        String
    )


    shop_type = Column(
        String
    )


    country = Column(
        String
    )


    currency = Column(
        String
    )


    monitoring = Column(
        Integer,
        default=1
    )


    prices = relationship(
        "Price",
        back_populates="product"
    )


    policies = relationship(
        "PricePolicy"
    )



# =========================
# Price Policy
# =========================

class PricePolicy(Base):

    __tablename__ = "price_policies"


    id = Column(
        Integer,
        primary_key=True
    )


    product_id = Column(
        Integer,
        ForeignKey(
            "products.id"
        )
    )


    country = Column(
        String
    )


    channel = Column(
        String
    )


    target_price = Column(
        Float
    )


    tolerance = Column(
        Float,
        default=10
    )



# =========================
# Price
# =========================

class Price(Base):

    __tablename__ = "prices"


    id = Column(
        Integer,
        primary_key=True
    )


    product_id = Column(
        Integer,
        ForeignKey(
            "products.id"
        )
    )


    price = Column(
        Float
    )


    date = Column(
        String
    )


    product = relationship(
        "Product",
        back_populates="prices"
    )



# =========================
# Collection Log
# =========================

class CollectionLog(Base):

    __tablename__ = "collection_logs"


    id = Column(
        Integer,
        primary_key=True
    )


    start_time = Column(
        String
    )


    end_time = Column(
        String
    )


    total_count = Column(
        Integer
    )


    success_count = Column(
        Integer
    )


    fail_count = Column(
        Integer
    )


    status = Column(
        String
    )



# =========================
# System Status
# =========================

class SystemStatus(Base):

    __tablename__ = "system_status"


    id = Column(
        Integer,
        primary_key=True
    )


    service = Column(
        String
    )


    status = Column(
        String
    )


    last_run = Column(
        String
    )


    message = Column(
        String
    )



# =========================
# Alert Rule
# =========================

class AlertRule(Base):

    __tablename__ = "alert_rules"


    id = Column(
        Integer,
        primary_key=True
    )


    product_id = Column(
        Integer
    )


    alert_type = Column(
        String
    )


    threshold = Column(
        Float
    )


    enabled = Column(
        Integer
    )



# =========================
# Alert
# =========================

class Alert(Base):

    __tablename__ = "alerts"


    id = Column(
        Integer,
        primary_key=True
    )


    # 추가
    priority = Column(
        String,
        default="NORMAL"
    )


    product_id = Column(
        Integer,
        ForeignKey(
            "products.id"
        )
    )


    alert_type = Column(
        String
    )


    old_price = Column(
        Float
    )


    new_price = Column(
        Float
    )


    change_rate = Column(
        Float
    )


    message = Column(
        String
    )


    status = Column(
        String,
        default="ACTIVE"
    )


    viewed_at = Column(
        String
    )


    resolved_at = Column(
        String
    )


    product = relationship(
        "Product"
    )



# =========================
# Collection Result
# =========================

class CollectionResult(Base):

    __tablename__ = "collection_results"

    id = Column(
        Integer,
        primary_key=True
    )

    collection_id = Column(
        Integer
    )

    product_id = Column(
        Integer
    )

    product = Column(
        String
    )

    channel = Column(
        String
    )

    shop_type = Column(
        String
    )

    status = Column(
        String
    )

    price = Column(
        Float
    )

    message = Column(
        String
    )

    created_at = Column(
        String
    )


def get_db():

    db = Session()

    try:

        yield db

    finally:

        db.close()


# =========================
# User / Role
# =========================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False,
        default="VIEWER"
    )

    active = Column(
        Integer,
        default=1
    )


# =========================
# Create Tables
# =========================

Base.metadata.create_all(engine)

