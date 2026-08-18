from database import Session, Alert


session = Session()


alerts = (
    session.query(Alert)
    .all()
)


for alert in alerts:

    print(
        "ID:",
        alert.id
    )

    print(
        "Product:",
        alert.product_id
    )

    print(
        "Old:",
        alert.old_price
    )

    print(
        "New:",
        alert.new_price
    )

    print(
        "Change:",
        alert.change_rate
    )

    print(
        "Type:",
        alert.alert_type
    )

    print(
        "Status:",
        alert.status
    )

    print(
        "Created:",
        alert.created_at
    )

    print("----------------")



session.close()