"""
KPI submission and retrieval endpoints
"""
from datetime import datetime, date, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from ..database import get_db
from ..models import Center, DailyMetric, TestSummary, SpeciesSummary, BreedSummary
from ..schemas import MetricsSubmission, CenterResponse, DailyMetricResponse

router = APIRouter(prefix="/kpi", tags=["KPI"])


@router.post("/submit", status_code=status.HTTP_201_CREATED)
def submit_metrics(metrics: MetricsSubmission, db: Session = Depends(get_db)):
    """
    Submit daily metrics from a center

    Authentication via API key
    """
    # Verify center and API key
    center = db.execute(
        select(Center).where(
            and_(
                Center.code == metrics.center_code,
                Center.api_key == metrics.api_key,
                Center.is_active == 1
            )
        )
    ).scalar_one_or_none()

    if not center:
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

    return {
        "message": "Metrics submitted successfully",
        "center": center.name,
        "date": metrics.date,
        "total_orders": metrics.total_orders
    }


@router.get("/centers", response_model=List[CenterResponse])
def list_centers(db: Session = Depends(get_db)):
    """List all registered centers"""
    centers = db.execute(select(Center)).scalars().all()
    return centers


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
