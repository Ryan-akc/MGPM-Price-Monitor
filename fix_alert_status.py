from database import Session, Alert


session = Session()


alerts = (
    session.query(Alert)
    .filter(
        Alert.status == "TRIGGERED"
    )
    .all()
)


for alert in alerts:

    alert.status = "NEW"


session.commit()


print(
    len(alerts),
    "alerts updated"
)


session.close()