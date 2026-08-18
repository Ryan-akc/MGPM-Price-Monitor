from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from database import (
    Session,
    Product,
    CollectionLog,
    CollectionResult,
    SystemStatus
)

from collector import collect_price

from alert_engine import check_system_alert


# =================================
# Scheduler
# =================================

scheduler = BackgroundScheduler()


# =================================
# System Status Update
# =================================

def update_system_status(
    db,
    service,
    status,
    message=""
):

    item = (
        db.query(SystemStatus)
        .filter(
            SystemStatus.service == service
        )
        .first()
    )

    now = datetime.now()

    if item:

        item.status = status
        item.last_run = str(now)
        item.message = message

    else:

        item = SystemStatus(
            service=service,
            status=status,
            last_run=str(now),
            message=message
        )

        db.add(item)

    db.commit()


# =================================
# Auto Collection
# =================================

def auto_collect():

    start_time = datetime.now()

    db = Session()

    success_count = 0
    fail_count = 0
    blocked_count = 0

    channel_stats = {}
    collection_results = []

    try:

        # =================================
        # Scheduler 시작 상태
        # =================================

        update_system_status(
            db,
            "Scheduler",
            "RUNNING",
            "Collection started"
        )

        # =================================
        # Collector 시작 상태
        # =================================

        update_system_status(
            db,
            "Collector",
            "RUNNING",
            "Collecting prices"
        )

        # =================================
        # Monitoring Products
        # =================================

        products = (
            db.query(Product)
            .filter(
                Product.monitoring == 1
            )
            .all()
        )

        print(
            f"Price Collection Started: "
            f"{len(products)} products"
        )

        # =================================
        # Collect Prices
        # =================================

        for product in products:

            channel = (
                product.channel
                or "Unknown"
            )

            shop_type = (
                product.shop_type
                or "Unknown"
            )

            product_name = (
                product.product
                or f"Product ID {product.id}"
            )

            # ---------------------------------
            # Channel Statistics
            # ---------------------------------

            if channel not in channel_stats:

                channel_stats[channel] = {
                    "total": 0,
                    "success": 0,
                    "fail": 0,
                    "blocked": 0,
                    "message": ""
                }

            channel_stats[channel]["total"] += 1

            try:

                # =================================
                # Collector 호출
                # =================================

                price = collect_price(
                    product.id
                )

                # =================================
                # Collection Success
                # =================================

                if price is not None:

                    success_count += 1

                    channel_stats[channel][
                        "success"
                    ] += 1

                    collection_results.append(
                        CollectionResult(
                            product_id=product.id,
                            product=product_name,
                            channel=channel,
                            shop_type=shop_type,
                            status="SUCCESS",
                            price=float(price),
                            message="Price collected successfully",
                            created_at=str(datetime.now())
                        )
                    )

                # =================================
                # Amazon Blocked
                # =================================

                elif shop_type.lower() == "amazon":

                    blocked_count += 1

                    channel_stats[channel][
                        "blocked"
                    ] += 1

                    error_message = (
                        f"{product_name}: "
                        "Amazon price collection blocked"
                    )

                    channel_stats[channel][
                        "message"
                    ] = error_message

                    collection_results.append(
                        CollectionResult(
                            product_id=product.id,
                            product=product_name,
                            channel=channel,
                            shop_type=shop_type,
                            status="BLOCKED",
                            price=None,
                            message="Amazon price collection blocked",
                            created_at=str(datetime.now())
                        )
                    )

                    print(
                        f"🚫 Collection Blocked | "
                        f"ID: {product.id} | "
                        f"Channel: {channel} | "
                        f"Product: {product_name} | "
                        f"Shop: {shop_type} | "
                        f"Reason: Amazon access blocked"
                    )

                # =================================
                # Collection Failed
                # =================================

                else:

                    fail_count += 1

                    channel_stats[channel][
                        "fail"
                    ] += 1

                    error_message = (
                        f"{product_name}: "
                        "No price data returned"
                    )

                    channel_stats[channel][
                        "message"
                    ] = error_message

                    collection_results.append(
                        CollectionResult(
                            product_id=product.id,
                            product=product_name,
                            channel=channel,
                            shop_type=shop_type,
                            status="FAILED",
                            price=None,
                            message="No price data returned",
                            created_at=str(datetime.now())
                        )
                    )

                    print(
                        f"❌ Collection Failed | "
                        f"ID: {product.id} | "
                        f"Channel: {channel} | "
                        f"Product: {product_name} | "
                        f"Shop: {shop_type} | "
                        f"Reason: No price data returned"
                    )

            except Exception as e:

                fail_count += 1

                channel_stats[channel][
                    "fail"
                ] += 1

                error_message = (
                    f"{product_name}: {str(e)}"
                )

                channel_stats[channel][
                    "message"
                ] = error_message

                collection_results.append(
                    CollectionResult(
                        product_id=product.id,
                        product=product_name,
                        channel=channel,
                        shop_type=shop_type,
                        status="FAILED",
                        price=None,
                        message=str(e),
                        created_at=str(datetime.now())
                    )
                )

                print(
                    f"❌ Collection Error | "
                    f"ID: {product.id} | "
                    f"Channel: {channel} | "
                    f"Product: {product_name} | "
                    f"Shop: {shop_type} | "
                    f"Error: {e}"
                )

        # =================================
        # Collection Result
        # =================================

        end_time = datetime.now()

        if fail_count == 0 and blocked_count == 0:

            status = "SUCCESS"

        elif fail_count == 0 and blocked_count > 0:

            status = "PARTIAL"

        elif success_count > 0:

            status = "PARTIAL"

        else:

            status = "FAILED"

        # =================================
        # Collection Summary Log
        # =================================

        print(
            f"Price Collection Completed | "
            f"Status: {status} | "
            f"Success: {success_count} | "
            f"Blocked: {blocked_count} | "
            f"Failed: {fail_count} | "
            f"Total: {len(products)}"
        )

        # =================================
        # Collection Log
        # =================================

        log = CollectionLog(

            start_time=str(start_time),

            end_time=str(end_time),

            total_count=len(products),

            success_count=success_count,

            fail_count=fail_count,

            status=status

        )

        db.add(log)

        # log.id 확보
        db.flush()

        # =================================
        # Collection Result 저장
        #
        # 각 Product × Channel 결과 기록
        # =================================

        for result in collection_results:

            result.collection_id = log.id

            db.add(result)

        db.commit()

        # =================================
        # Overall Collector Status
        # =================================

        if len(products) == 0:

            collector_message = (
                "No monitoring products"
            )

        elif status == "FAILED":

            collector_message = (
                "All collectors failed"
            )

        elif blocked_count > 0:

            collector_message = (
                f"{success_count}/{len(products)} "
                f"products collected | "
                f"{blocked_count} blocked | "
                f"{fail_count} failed"
            )

        else:

            collector_message = (
                f"{success_count}/{len(products)} "
                "products collected"
            )

        update_system_status(

            db,

            "Collector",

            status,

            collector_message

        )

        # =================================
        # Channel Collector Status
        # =================================

        for channel, stat in channel_stats.items():

            # ---------------------------------
            # Channel Status
            # ---------------------------------

            if (
                stat["fail"] == 0
                and stat["blocked"] == 0
            ):

                channel_status = "SUCCESS"

            elif stat["success"] > 0:

                channel_status = "PARTIAL"

            elif stat["blocked"] > 0:

                channel_status = "BLOCKED"

            else:

                channel_status = "FAILED"

            # ---------------------------------
            # Channel Message
            # ---------------------------------

            if stat["blocked"] > 0:

                message = (
                    f"{stat['success']}/{stat['total']} "
                    f"products collected | "
                    f"{stat['blocked']} blocked"
                )

            elif stat["fail"] > 0:

                message = stat["message"]

            else:

                message = (
                    f"{stat['success']}/{stat['total']} "
                    "products collected"
                )

            # ---------------------------------
            # Save Channel Status
            # ---------------------------------

            update_system_status(

                db,

                f"{channel} Collector",

                channel_status,

                message

            )

        # =================================
        # Scheduler Completed
        # =================================

        update_system_status(

            db,

            "Scheduler",

            "SUCCESS",

            "Waiting next schedule"

        )

        # =================================
        # System Alert
        # =================================

        check_system_alert(db)

    except Exception as e:

        print(
            f"❌ Scheduler Error: {e}"
        )

        # =================================
        # Scheduler Failure
        # =================================

        try:

            update_system_status(

                db,

                "Scheduler",

                "FAILED",

                str(e)

            )

        except Exception:

            pass

        # =================================
        # Collector Failure
        # =================================

        try:

            update_system_status(

                db,

                "Collector",

                "FAILED",

                str(e)

            )

        except Exception:

            pass

        # =================================
        # System Alert
        # =================================

        try:

            check_system_alert(db)

        except Exception as alert_error:

            print(
                f"System Alert Error: "
                f"{alert_error}"
            )

    finally:

        # =================================
        # Close Database Session
        # =================================

        db.close()


# =================================
# Start Scheduler
# =================================

def start_scheduler():

    if not scheduler.running:

        scheduler.add_job(

            auto_collect,

            "interval",

            hours=6,

            id="price_monitor",

            replace_existing=True,

            max_instances=1,

            coalesce=True,

            misfire_grace_time=30

        )

        scheduler.start()

        db = Session()

        try:

            update_system_status(

                db,

                "Scheduler",

                "RUNNING",

                "Scheduler started"

            )

        finally:

            db.close()

        print(
            "Price Monitor Scheduler Started"
        )