from database import (
    Session,
    Product,
    AlertRule
)


session = Session()


product = (
    session.query(Product)
    .first()
)


if product:


    rule = AlertRule(

        product_id=product.id,

        alert_type="DROP_PERCENT",

        threshold=-5,

        enabled=1

    )


    session.add(rule)

    session.commit()


    print(
        "Alert Rule Created:",
        product.product
    )


else:

    print(
        "Product not found"
    )


session.close()