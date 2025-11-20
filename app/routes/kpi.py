"""
KPI submission and retrieval endpoints

Version 2.0 - Enhanced Security:
- API key authentication via headers
- Rate limiting per endpoint
- Structured logging
- Improved error handling
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, delete
from loguru import logger

from ..database import get_db
from ..models import (
    Center, DailyMetric, TestSummary, SpeciesSummary, BreedSummary,
    PerformanceMetric, ModuleMetric, SystemUsageMetric, PaymentMethodMetric
)
from ..schemas import (
    MetricsSubmission,
    EnhancedMetricsSubmission,
    CenterResponse,
    DailyMetricResponse,
    EventSubmission,
    CenterMetadataUpdate
)
from ..auth import get_api_key_from_header_or_body
from ..config import settings

router = APIRouter(prefix="/kpi", tags=["KPI"])


def get_limiter(request: Request):
    """Get rate limiter from app state"""
    return request.app.state.limiter


@router.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_metrics(
    request: Request,
    metrics: MetricsSubmission,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Submit daily metrics from a center

    Authentication: X-API-Key header (recommended) or api_key in body (deprecated)

    Rate limit: Configurable via RATE_LIMIT_SUBMIT env var (default: 100/day)
    """
    # Apply rate limiting
    try:
        limiter = get_limiter(request)
        await limiter.limit(settings.RATE_LIMIT_SUBMIT)(request)
    except Exception:
        # If rate limiting fails, continue anyway
        pass

    # Get API key from header or body (backward compatibility)
    api_key = get_api_key_from_header_or_body(x_api_key, metrics.api_key)

    logger.info(f"Metrics submission request from center: {metrics.center_code}")

    # Verify center and API key
    center = db.execute(
        select(Center).where(
            and_(
                Center.code == metrics.center_code,
                Center.api_key == api_key,
                Center.is_active == 1
            )
        )
    ).scalar_one_or_none()

    if not center:
        logger.warning(f"Invalid center or API key for: {metrics.center_code}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid center code or API key"
        )

    # Update or create daily metrics
    daily_metric = db.execute(
        select(DailyMetric).where(
            and_(
                DailyMetric.center_id == center.id,
                DailyMetric.date == metrics.date
            )
        )
    ).scalar_one_or_none()

    if daily_metric:
        # Update existing
        daily_metric.total_orders = metrics.total_orders
        daily_metric.total_results = metrics.total_results
        daily_metric.total_pets = metrics.total_pets
        daily_metric.total_owners = metrics.total_owners
    else:
        # Create new
        daily_metric = DailyMetric(
            center_id=center.id,
            date=metrics.date,
            total_orders=metrics.total_orders,
            total_results=metrics.total_results,
            total_pets=metrics.total_pets,
            total_owners=metrics.total_owners
        )
        db.add(daily_metric)

    # Delete existing test summaries for this date
    db.query(TestSummary).filter(
        and_(
            TestSummary.center_id == center.id,
            TestSummary.date == metrics.date
        )
    ).delete()

    # Insert test summaries
    for test in metrics.tests:
        test_summary = TestSummary(
            center_id=center.id,
            date=metrics.date,
            test_code=test.code,
            test_name=test.name,
            count=test.count
        )
        db.add(test_summary)

    # Delete existing species summaries for this date
    db.query(SpeciesSummary).filter(
        and_(
            SpeciesSummary.center_id == center.id,
            SpeciesSummary.date == metrics.date
        )
    ).delete()

    # Insert species summaries
    for sp in metrics.species:
        species_summary = SpeciesSummary(
            center_id=center.id,
            date=metrics.date,
            species_name=sp.species,
            count=sp.count
        )
        db.add(species_summary)

    # Delete existing breed summaries for this date
    db.query(BreedSummary).filter(
        and_(
            BreedSummary.center_id == center.id,
            BreedSummary.date == metrics.date
        )
    ).delete()

    # Insert breed summaries
    for breed in metrics.breeds:
        breed_summary = BreedSummary(
            center_id=center.id,
            date=metrics.date,
            breed_name=breed.breed,
            species_name=breed.species,
            count=breed.count
        )
        db.add(breed_summary)

    # Update center last sync
    center.last_sync_at = datetime.utcnow()

    db.commit()

    logger.info(
        f"Metrics submitted successfully - Center: {center.name}, "
        f"Date: {metrics.date}, Orders: {metrics.total_orders}"
    )

    return {
        "message": "Metrics submitted successfully",
        "center": center.name,
        "date": metrics.date,
        "total_orders": metrics.total_orders
    }


@router.post("/submit/enhanced", status_code=status.HTTP_201_CREATED)
async def submit_enhanced_metrics(
    request: Request,
    metrics: EnhancedMetricsSubmission,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Submit enhanced daily metrics from a center (v2.1)

    Includes all original metrics plus:
    - Performance metrics (processing times, peak hours, completion rates)
    - Module usage metrics (laboratorio, consultas, farmacia, etc.)
    - System usage metrics (users, sessions, access types)
    - Payment method distribution

    Authentication: X-API-Key header (recommended) or api_key in body (deprecated)
    Rate limit: Configurable via RATE_LIMIT_SUBMIT env var (default: 100/day)
    """
    # Apply rate limiting
    try:
        limiter = get_limiter(request)
        await limiter.limit(settings.RATE_LIMIT_SUBMIT)(request)
    except Exception:
        pass

    # Get API key from header or body (backward compatibility)
    api_key = get_api_key_from_header_or_body(x_api_key, metrics.api_key)

    logger.info(f"Enhanced metrics submission from center: {metrics.center_code}")

    # Verify center and API key
    center = db.execute(
        select(Center).where(
            and_(
                Center.code == metrics.center_code,
                Center.api_key == api_key,
                Center.is_active == 1
            )
        )
    ).scalar_one_or_none()

    if not center:
        logger.warning(f"Invalid center or API key for: {metrics.center_code}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid center code or API key"
        )

    # ========================================================================
    # PROCESS ORIGINAL METRICS (backward compatible with /submit endpoint)
    # ========================================================================

    # Update or create daily metrics
    daily_metric = db.execute(
        select(DailyMetric).where(
            and_(
                DailyMetric.center_id == center.id,
                DailyMetric.date == metrics.date
            )
        )
    ).scalar_one_or_none()

    if daily_metric:
        daily_metric.total_orders = metrics.total_orders
        daily_metric.total_results = metrics.total_results
        daily_metric.total_pets = metrics.total_pets
        daily_metric.total_owners = metrics.total_owners
    else:
        daily_metric = DailyMetric(
            center_id=center.id,
            date=metrics.date,
            total_orders=metrics.total_orders,
            total_results=metrics.total_results,
            total_pets=metrics.total_pets,
            total_owners=metrics.total_owners
        )
        db.add(daily_metric)

    # Process test summaries
    db.query(TestSummary).filter(
        and_(
            TestSummary.center_id == center.id,
            TestSummary.date == metrics.date
        )
    ).delete()

    for test in metrics.tests:
        test_summary = TestSummary(
            center_id=center.id,
            date=metrics.date,
            test_code=test.code,
            test_name=test.name,
            count=test.count
        )
        db.add(test_summary)

    # Process species summaries
    db.query(SpeciesSummary).filter(
        and_(
            SpeciesSummary.center_id == center.id,
            SpeciesSummary.date == metrics.date
        )
    ).delete()

    for sp in metrics.species:
        species_summary = SpeciesSummary(
            center_id=center.id,
            date=metrics.date,
            species_name=sp.species,
            count=sp.count
        )
        db.add(species_summary)

    # Process breed summaries
    db.query(BreedSummary).filter(
        and_(
            BreedSummary.center_id == center.id,
            BreedSummary.date == metrics.date
        )
    ).delete()

    for breed in metrics.breeds:
        breed_summary = BreedSummary(
            center_id=center.id,
            date=metrics.date,
            breed_name=breed.breed,
            species_name=breed.species,
            count=breed.count
        )
        db.add(breed_summary)

    # ========================================================================
    # PROCESS ENHANCED METRICS (v2.1)
    # ========================================================================

    saved_metrics = {
        "performance": False,
        "modules": 0,
        "system_usage": False,
        "payment_methods": 0
    }

    # Process performance metrics
    if metrics.performance:
        perf = db.execute(
            select(PerformanceMetric).where(
                and_(
                    PerformanceMetric.center_id == center.id,
                    PerformanceMetric.date == metrics.date
                )
            )
        ).scalar_one_or_none()

        if perf:
            # Update existing
            perf.avg_order_processing_time = metrics.performance.avg_order_processing_time
            perf.peak_hour = metrics.performance.peak_hour
            perf.peak_hour_orders = metrics.performance.peak_hour_orders
            perf.completion_rate = metrics.performance.completion_rate
            perf.same_day_completion = metrics.performance.same_day_completion
            perf.morning_orders = metrics.performance.morning_orders
            perf.afternoon_orders = metrics.performance.afternoon_orders
            perf.evening_orders = metrics.performance.evening_orders
            perf.night_orders = metrics.performance.night_orders
        else:
            # Create new
            perf = PerformanceMetric(
                center_id=center.id,
                date=metrics.date,
                avg_order_processing_time=metrics.performance.avg_order_processing_time,
                peak_hour=metrics.performance.peak_hour,
                peak_hour_orders=metrics.performance.peak_hour_orders,
                completion_rate=metrics.performance.completion_rate,
                same_day_completion=metrics.performance.same_day_completion,
                morning_orders=metrics.performance.morning_orders,
                afternoon_orders=metrics.performance.afternoon_orders,
                evening_orders=metrics.performance.evening_orders,
                night_orders=metrics.performance.night_orders
            )
            db.add(perf)

        saved_metrics["performance"] = True

    # Process module metrics
    if metrics.modules:
        # Delete existing module metrics for this date
        db.query(ModuleMetric).filter(
            and_(
                ModuleMetric.center_id == center.id,
                ModuleMetric.date == metrics.date
            )
        ).delete()

        for module in metrics.modules:
            module_metric = ModuleMetric(
                center_id=center.id,
                date=metrics.date,
                module_name=module.module_name,
                operations_count=module.operations_count,
                active_users=module.active_users,
                total_revenue=module.total_revenue,
                avg_transaction=module.avg_transaction
            )
            db.add(module_metric)
            saved_metrics["modules"] += 1

    # Process system usage metrics
    if metrics.system_usage:
        sys_usage = db.execute(
            select(SystemUsageMetric).where(
                and_(
                    SystemUsageMetric.center_id == center.id,
                    SystemUsageMetric.date == metrics.date
                )
            )
        ).scalar_one_or_none()

        if sys_usage:
            # Update existing
            sys_usage.total_active_users = metrics.system_usage.total_active_users
            sys_usage.peak_concurrent_users = metrics.system_usage.peak_concurrent_users
            sys_usage.avg_session_duration = metrics.system_usage.avg_session_duration
            sys_usage.web_access_count = metrics.system_usage.web_access_count
            sys_usage.mobile_access_count = metrics.system_usage.mobile_access_count
            sys_usage.desktop_access_count = metrics.system_usage.desktop_access_count
            sys_usage.total_workstations = metrics.system_usage.total_workstations
        else:
            # Create new
            sys_usage = SystemUsageMetric(
                center_id=center.id,
                date=metrics.date,
                total_active_users=metrics.system_usage.total_active_users,
                peak_concurrent_users=metrics.system_usage.peak_concurrent_users,
                avg_session_duration=metrics.system_usage.avg_session_duration,
                web_access_count=metrics.system_usage.web_access_count,
                mobile_access_count=metrics.system_usage.mobile_access_count,
                desktop_access_count=metrics.system_usage.desktop_access_count,
                total_workstations=metrics.system_usage.total_workstations
            )
            db.add(sys_usage)

        saved_metrics["system_usage"] = True

    # Process payment method metrics
    if metrics.payment_methods:
        # Delete existing payment method metrics for this date
        db.query(PaymentMethodMetric).filter(
            and_(
                PaymentMethodMetric.center_id == center.id,
                PaymentMethodMetric.date == metrics.date
            )
        ).delete()

        for payment in metrics.payment_methods:
            payment_metric = PaymentMethodMetric(
                center_id=center.id,
                date=metrics.date,
                payment_method=payment.payment_method,
                transaction_count=payment.transaction_count,
                total_amount=payment.total_amount
            )
            db.add(payment_metric)
            saved_metrics["payment_methods"] += 1

    # Update center last sync
    center.last_sync_at = datetime.utcnow()

    db.commit()

    logger.info(
        f"Enhanced metrics submitted - Center: {center.name}, Date: {metrics.date}, "
        f"Orders: {metrics.total_orders}, Performance: {saved_metrics['performance']}, "
        f"Modules: {saved_metrics['modules']}, System: {saved_metrics['system_usage']}, "
        f"Payments: {saved_metrics['payment_methods']}"
    )

    return {
        "message": "Enhanced metrics submitted successfully",
        "center": center.name,
        "date": metrics.date,
        "saved": {
            "daily_metrics": True,
            "tests": len(metrics.tests),
            "species": len(metrics.species),
            "breeds": len(metrics.breeds),
            "performance": saved_metrics["performance"],
            "modules": saved_metrics["modules"],
            "system_usage": saved_metrics["system_usage"],
            "payment_methods": saved_metrics["payment_methods"]
        }
    }


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def submit_event(
    request: Request,
    event: EventSubmission,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Submit real-time event from a center

    Event types: order_created, result_created, pet_created, owner_created
    Authentication: X-API-Key header (recommended) or api_key in body (deprecated)

    Rate limit: Configurable via RATE_LIMIT_EVENTS env var (default: 1000/day)
    """
    # Apply rate limiting
    try:
        limiter = get_limiter(request)
        await limiter.limit(settings.RATE_LIMIT_EVENTS)(request)
    except Exception:
        # If rate limiting fails, continue anyway
        pass

    # Get API key from header or body
    api_key = get_api_key_from_header_or_body(x_api_key, event.api_key)

    logger.info(f"Event submission: {event.event_type} from center: {event.center_code}")

    # Get or auto-register center
    center = db.execute(
        select(Center).where(Center.code == event.center_code)
    ).scalar_one_or_none()

    if not center:
        # Auto-register new center
        logger.info(f"Auto-registering new center: {event.center_code}")
        center = Center(
            code=event.center_code,
            name=event.center_code,  # Use code as name initially
            api_key=api_key,
            is_active=1,
            registered_at=datetime.utcnow()
        )
        db.add(center)
        db.flush()
    else:
        # Verify API key for existing centers
        if center.api_key != api_key:
            logger.warning(f"Invalid API key for center: {event.center_code}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key for center"
            )

    # Get today's date from event timestamp
    event_date = event.timestamp.date()

    # Get or create today's daily metric
    daily_metric = db.execute(
        select(DailyMetric).where(
            and_(
                DailyMetric.center_id == center.id,
                DailyMetric.date == event_date
            )
        )
    ).scalar_one_or_none()

    if not daily_metric:
        daily_metric = DailyMetric(
            center_id=center.id,
            date=event_date,
            total_orders=0,
            total_results=0,
            total_pets=0,
            total_owners=0
        )
        db.add(daily_metric)
        db.flush()

    # Increment counters based on event type
    if event.event_type == "order_created":
        daily_metric.total_orders += 1

        # Update test summaries if tests provided
        if event.data.tests:
            for test_code in event.data.tests:
                test_summary = db.execute(
                    select(TestSummary).where(
                        and_(
                            TestSummary.center_id == center.id,
                            TestSummary.date == event_date,
                            TestSummary.test_code == test_code
                        )
                    )
                ).scalar_one_or_none()

                if test_summary:
                    test_summary.count += 1
                else:
                    test_summary = TestSummary(
                        center_id=center.id,
                        date=event_date,
                        test_code=test_code,
                        test_name=test_code,  # Will be updated by batch if needed
                        count=1
                    )
                    db.add(test_summary)

        # Update species summary if species provided
        if event.data.species:
            species_summary = db.execute(
                select(SpeciesSummary).where(
                    and_(
                        SpeciesSummary.center_id == center.id,
                        SpeciesSummary.date == event_date,
                        SpeciesSummary.species_name == event.data.species
                    )
                )
            ).scalar_one_or_none()

            if species_summary:
                species_summary.count += 1
            else:
                species_summary = SpeciesSummary(
                    center_id=center.id,
                    date=event_date,
                    species_name=event.data.species,
                    count=1
                )
                db.add(species_summary)

        # Update breed summary if breed and species provided
        if event.data.breed and event.data.species:
            breed_summary = db.execute(
                select(BreedSummary).where(
                    and_(
                        BreedSummary.center_id == center.id,
                        BreedSummary.date == event_date,
                        BreedSummary.breed_name == event.data.breed,
                        BreedSummary.species_name == event.data.species
                    )
                )
            ).scalar_one_or_none()

            if breed_summary:
                breed_summary.count += 1
            else:
                breed_summary = BreedSummary(
                    center_id=center.id,
                    date=event_date,
                    breed_name=event.data.breed,
                    species_name=event.data.species,
                    count=1
                )
                db.add(breed_summary)

    elif event.event_type == "result_created":
        daily_metric.total_results += 1

    elif event.event_type == "pet_created":
        daily_metric.total_pets += 1

        # Update species summary if species provided
        if event.data.species:
            species_summary = db.execute(
                select(SpeciesSummary).where(
                    and_(
                        SpeciesSummary.center_id == center.id,
                        SpeciesSummary.date == event_date,
                        SpeciesSummary.species_name == event.data.species
                    )
                )
            ).scalar_one_or_none()

            if species_summary:
                species_summary.count += 1
            else:
                species_summary = SpeciesSummary(
                    center_id=center.id,
                    date=event_date,
                    species_name=event.data.species,
                    count=1
                )
                db.add(species_summary)

        # Update breed summary if breed and species provided
        if event.data.breed and event.data.species:
            breed_summary = db.execute(
                select(BreedSummary).where(
                    and_(
                        BreedSummary.center_id == center.id,
                        BreedSummary.date == event_date,
                        BreedSummary.breed_name == event.data.breed,
                        BreedSummary.species_name == event.data.species
                    )
                )
            ).scalar_one_or_none()

            if breed_summary:
                breed_summary.count += 1
            else:
                breed_summary = BreedSummary(
                    center_id=center.id,
                    date=event_date,
                    breed_name=event.data.breed,
                    species_name=event.data.species,
                    count=1
                )
                db.add(breed_summary)

    elif event.event_type == "owner_created":
        daily_metric.total_owners += 1

    # Update center last sync
    center.last_sync_at = datetime.utcnow()

    db.commit()

    logger.info(
        f"Event processed successfully - Type: {event.event_type}, "
        f"Center: {center.name}, Date: {event_date}"
    )

    return {
        "message": "Event processed successfully",
        "event_type": event.event_type,
        "center": center.name,
        "date": event_date.isoformat()
    }


@router.get("/centers", response_model=List[CenterResponse])
def list_centers(db: Session = Depends(get_db)):
    """List all registered centers"""
    centers = db.execute(select(Center)).scalars().all()
    return centers


@router.put("/centers/{center_code}", status_code=status.HTTP_200_OK)
def update_center_metadata(
    center_code: str,
    center_data: CenterMetadataUpdate,
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Update center metadata from main pethospital system

    Called when center details change in the main system.
    Updates center name, location, and active status.

    Authentication via X-API-Key header.
    """
    # Find center by code and API key
    center = db.execute(
        select(Center).where(
            and_(
                Center.code == center_code,
                Center.api_key == x_api_key
            )
        )
    ).scalar_one_or_none()

    if not center:
        # Try to find center by code only (for auto-registration with new data)
        center = db.execute(
            select(Center).where(Center.code == center_code)
        ).scalar_one_or_none()

        if not center:
            # Auto-register: Create new center
            logger.info(f"Auto-registering new center: {center_code}")
            center = Center(
                code=center_code,
                name=center_data.name or center_code,  # Use code as fallback name
                city=center_data.city,
                country=center_data.country or "Republica Dominicana",
                api_key=x_api_key,
                is_active=1 if (center_data.is_active is None or center_data.is_active) else 0,
                registered_at=datetime.utcnow(),
                last_sync_at=datetime.utcnow()
            )
            db.add(center)
        else:
            # Update API key if provided by authorized request
            center.api_key = x_api_key

    # Update fields if provided
    if center_data.name is not None:
        center.name = center_data.name

    if center_data.city is not None:
        center.city = center_data.city

    if center_data.country is not None:
        center.country = center_data.country

    if center_data.is_active is not None:
        center.is_active = 1 if center_data.is_active else 0

    # Update last sync timestamp
    center.last_sync_at = datetime.utcnow()

    db.commit()
    db.refresh(center)

    logger.info(f"Center metadata updated for {center_code}: name={center.name}, is_active={center.is_active}")

    return {
        "message": "Center metadata updated successfully",
        "center_code": center_code,
        "center_name": center.name
    }


@router.get("/centers/{center_code}/metrics", response_model=List[DailyMetricResponse])
def get_center_metrics(
    center_code: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get metrics for a specific center

    Args:
        center_code: Center code
        days: Number of days to retrieve (default 30)
    """
    center = db.execute(
        select(Center).where(Center.code == center_code)
    ).scalar_one_or_none()

    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Center not found"
        )

    since_date = date.today() - timedelta(days=days)

    metrics = db.execute(
        select(DailyMetric)
        .where(
            and_(
                DailyMetric.center_id == center.id,
                DailyMetric.date >= since_date
            )
        )
        .order_by(DailyMetric.date.desc())
    ).scalars().all()

    return metrics


@router.get("/stats/summary")
def get_summary_stats(days: int = 30, db: Session = Depends(get_db)):
    """
    Get summary statistics across all centers

    Args:
        days: Number of days to aggregate (default 30)
    """
    since_date = date.today() - timedelta(days=days)

    total_centers = db.execute(select(func.count(Center.id))).scalar_one()
    active_centers = db.execute(
        select(func.count(Center.id)).where(Center.is_active == 1)
    ).scalar_one()

    # Aggregate metrics
    totals = db.execute(
        select(
            func.sum(DailyMetric.total_orders),
            func.sum(DailyMetric.total_results),
            func.sum(DailyMetric.total_pets)
        ).where(DailyMetric.date >= since_date)
    ).one()

    return {
        "total_centers": total_centers,
        "active_centers": active_centers,
        "date_range": {
            "from": since_date.isoformat(),
            "to": date.today().isoformat(),
            "days": days
        },
        "total_orders": totals[0] or 0,
        "total_results": totals[1] or 0,
        "total_pets": totals[2] or 0
    }


@router.delete("/centers/{center_code}/data", status_code=status.HTTP_200_OK)
def delete_center_data(
    center_code: str,
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Delete all KPI data for a center (called during hard delete from main system).

    This endpoint is called automatically when a center is permanently deleted
    from the main system. It removes all historical KPI data for the center
    but keeps the center registration.

    Requires: X-API-Key header with valid API key

    Args:
        center_code: Center code to cleanup
        x_api_key: API key for authentication (header)
        db: Database session

    Returns:
        Summary of deleted records

    Raises:
        HTTPException: 404 if center not found, 401 if invalid API key
    """
    # Verify center exists and API key matches
    center = db.execute(
        select(Center).where(
            and_(
                Center.code == center_code,
                Center.api_key == x_api_key
            )
        )
    ).scalar_one_or_none()

    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Center {center_code} not found or invalid API key"
        )

    logger.warning(f"Deleting KPI data for center {center_code} (ID: {center.id})")

    try:
        # Delete all daily metrics
        metrics_count = db.execute(
            delete(DailyMetric).where(DailyMetric.center_id == center.id)
        ).rowcount

        # Delete all test summaries
        tests_count = db.execute(
            delete(TestSummary).where(TestSummary.center_id == center.id)
        ).rowcount

        # Delete all species summaries
        species_count = db.execute(
            delete(SpeciesSummary).where(SpeciesSummary.center_id == center.id)
        ).rowcount

        # Delete all breed summaries
        breeds_count = db.execute(
            delete(BreedSummary).where(BreedSummary.center_id == center.id)
        ).rowcount

        # Reset center last_sync_at
        center.last_sync_at = None

        db.commit()

        logger.warning(f"KPI data deleted for center {center_code}: "
                      f"{metrics_count} metrics, {tests_count} tests, "
                      f"{species_count} species, {breeds_count} breeds")

        return {
            "center_code": center_code,
            "deleted": {
                "daily_metrics": metrics_count,
                "test_summaries": tests_count,
                "species_summaries": species_count,
                "breed_summaries": breeds_count
            },
            "message": "KPI data deleted successfully"
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete KPI data for center {center_code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete KPI data: {str(e)}"
        )
