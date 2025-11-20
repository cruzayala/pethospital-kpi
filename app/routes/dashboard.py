"""
Dashboard routes with HTML rendering

Version 4.0 - Full Server-Side Authentication:
- All protected routes require JWT authentication server-side
- Rate limiting
- Structured logging
- Login page (public)
- 401 error page
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from loguru import logger

from ..database import get_db
from ..models import Center, DailyMetric, TestSummary, SpeciesSummary, User
from ..config import settings
from ..rate_limiter import limiter
from ..auth import get_current_user

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request
):
    """
    Login page (public access)
    """
    return templates.TemplateResponse("login.html", {
        "request": request
    })


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Settings page - PROTECTED

    **PROTECTED**: Requires server-side authentication
    Only authenticated users can access system settings
    """
    logger.info(f"Settings page accessed by: {current_user.username}")
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "current_user": current_user
    })


@router.get("/", response_class=HTMLResponse)
@limiter.limit(settings.RATE_LIMIT_DASHBOARD)
async def dashboard_home(
    request: Request,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Main dashboard page with charts and stats

    **PROTECTED**: Requires server-side authentication
    Rate limit: Configurable via RATE_LIMIT_DASHBOARD env var (default: 60/minute)
    """
    logger.info(f"Dashboard accessed by {current_user.username} - days: {days}")

    since_date = date.today() - timedelta(days=days)

    # Get all centers
    centers = db.execute(select(Center)).scalars().all()

    # Get aggregate stats
    totals = db.execute(
        select(
            func.sum(DailyMetric.total_orders),
            func.sum(DailyMetric.total_results),
            func.sum(DailyMetric.total_pets)
        ).where(DailyMetric.date >= since_date)
    ).one()

    # Get daily trend (last 30 days)
    daily_trend = db.execute(
        select(
            DailyMetric.date,
            func.sum(DailyMetric.total_orders).label("orders"),
            func.sum(DailyMetric.total_results).label("results")
        )
        .where(DailyMetric.date >= since_date)
        .group_by(DailyMetric.date)
        .order_by(DailyMetric.date)
    ).all()

    # Get per-center stats
    center_stats = []
    for center in centers:
        center_totals = db.execute(
            select(
                func.sum(DailyMetric.total_orders),
                func.sum(DailyMetric.total_results),
                func.sum(DailyMetric.total_pets)
            )
            .where(
                and_(
                    DailyMetric.center_id == center.id,
                    DailyMetric.date >= since_date
                )
            )
        ).one()

        center_stats.append({
            "center": center,
            "orders": center_totals[0] or 0,
            "results": center_totals[1] or 0,
            "pets": center_totals[2] or 0
        })

    # Get top tests across all centers
    top_tests = db.execute(
        select(
            TestSummary.test_code,
            TestSummary.test_name,
            func.sum(TestSummary.count).label("total")
        )
        .where(TestSummary.date >= since_date)
        .group_by(TestSummary.test_code, TestSummary.test_name)
        .order_by(func.sum(TestSummary.count).desc())
        .limit(10)
    ).all()

    # Get species distribution
    species_dist = db.execute(
        select(
            SpeciesSummary.species_name,
            func.sum(SpeciesSummary.count).label("total")
        )
        .where(SpeciesSummary.date >= since_date)
        .group_by(SpeciesSummary.species_name)
        .order_by(func.sum(SpeciesSummary.count).desc())
    ).all()

    return templates.TemplateResponse("dashboard_v4_interactive.html", {
        "request": request,
        "days": days,
        "date_from": since_date.isoformat(),
        "date_to": date.today().isoformat(),
        "total_centers": len(centers),
        "active_centers": sum(1 for c in centers if c.is_active),
        "total_orders": totals[0] or 0,
        "total_results": totals[1] or 0,
        "total_pets": totals[2] or 0,
        "centers": centers,
        "center_stats": center_stats,
        "daily_trend": daily_trend,
        "top_tests": top_tests,
        "species_dist": species_dist,
        "current_user": current_user  # Now passing authenticated user from server
    })

