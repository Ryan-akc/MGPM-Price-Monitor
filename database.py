from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import UniqueConstraint


engine = create_engine(
    "sqlite:///price_monitor.db",
    echo=False
)

print(engine.url)

Session = sessionmaker(bind=engine)

Base = declarative_base()


# ======================
# 상품 테이블
# ======================

class Product(Base):

    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True
    )

    channel = Column(String)

    product = Column(String)

    url = Column(String)

    shop_type = Column(String)

    country = Column(String)

    currency = Column(String)

    monitoring = Column(
        Integer,
        default=1
    )


# ======================
# 가격 이력 테이블
# ======================

class Price(Base):

    __tablename__ = "prices"

    id = Column(
        Integer,
        primary_key=True
    )

    product_id = Column(
        Integer
    )

    price = Column(
        Float
    )

    date = Column(
        String
    )


    # 같은 상품 + 같은 가격 중복 방지
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "price",
            name="unique_product_price"
        ),
    )


# ======================
# 자동 수집 로그 테이블
# ======================

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


# ======================
# DB 테이블 생성
# ======================

Base.metadata.create_all(engine)