from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from database import Session, Product, CollectionLog
from collector import collect_price


scheduler = BackgroundScheduler()


def auto_collect():

    start_time = datetime.now()

    db = Session()

    success_count = 0
    fail_count = 0

    try:

        products = db.query(Product).filter(
            Product.monitoring == 1
        ).all()


        print(
            f"[{start_time}] Monitoring {len(products)} products"
        )


        for product in products:

            try:

                price = collect_price(
                    product.id
                )


                if price:

                    success_count += 1

                    print(
                        f"수집 완료: {product.product} {price}"
                    )

                else:

                    fail_count += 1

                    print(
                        f"수집 실패: {product.product}"
                    )


            except Exception as e:

                fail_count += 1

                print(
                    f"Collect Error - {product.product}: {e}"
                )


        end_time = datetime.now()


        if fail_count == 0:

            status = "SUCCESS"

        elif success_count > 0:

            status = "PARTIAL"

        else:

            status = "FAIL"



        log = CollectionLog(

            start_time=str(start_time),

            end_time=str(end_time),

            total_count=len(products),

            success_count=success_count,

            fail_count=fail_count,

            status=status
        )


        db.add(log)

        db.commit()



        print(
            f"""
===== Auto Collection Finished =====
Start : {start_time}
End   : {end_time}
Total : {len(products)}
Success : {success_count}
Fail : {fail_count}
Status : {status}
====================================
"""
        )


    except Exception as e:

        print(
            f"Scheduler Error: {e}"
        )


    finally:

        db.close()



def start_scheduler():

    if not scheduler.running:

        scheduler.add_job(

            auto_collect,

            "interval",

            seconds=30,

            id="price_monitor",

            replace_existing=True

        )


        scheduler.start()


        print(
            "Price Monitor Scheduler Started"
        )


        print(
            "Next Run:",
            scheduler.get_job(
                "price_monitor"
            ).next_run_time
        )