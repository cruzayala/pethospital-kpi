# coding: utf-8
"""
Centers Analytics Module

Provides comprehensive analytics and insights for veterinary centers including:
- Performance comparisons
- Growth trends
- Activity metrics
- Ranking and benchmarking
"""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, desc, case
from loguru import logger

from ..models import (
    Center, DailyMetric, TestSummary, SpeciesSummary, BreedSummary,
    PerformanceMetric, ModuleMetric, SystemUsageMetric, PaymentMethodMetric
)


class CentersAnalytics:
    """Analytics for veterinary centers"""

    def __init__(self, db: Session):
        self.db = db

    def get_center_summary(self, center_code: str, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive summary for a specific center

        Returns:
            - Basic info
            - Total metrics (orders, results, pets, owners)
            - Average daily metrics
            - Top tests
            - Species distribution
            - Performance indicators
        """
        logger.info(f"Generating summary for center: {center_code}")

        # Get center
        center = self.db.execute(
            select(Center).where(Center.code == center_code)
        ).scalar_one_or_none()

        if not center:
            return None

        since_date = date.today() - timedelta(days=days)

        # Basic metrics
        totals = self.db.execute(
            select(
                func.count(DailyMetric.id).label("days_with_data"),
                func.sum(DailyMetric.total_orders).label("total_orders"),
                func.sum(DailyMetric.total_results).label("total_results"),
                func.sum(DailyMetric.total_pets).label("total_pets"),
                func.sum(DailyMetric.total_owners).label("total_owners"),
                func.avg(DailyMetric.total_orders).label("avg_orders"),
                func.max(DailyMetric.total_orders).label("max_orders"),
                func.min(DailyMetric.total_orders).label("min_orders")
            )
            .where(
                and_(
                    DailyMetric.center_id == center.id,
                    DailyMetric.date >= since_date
                )
            )
        ).one()

        # Top tests
        top_tests = self.db.execute(
            select(
                TestSummary.test_code,
                TestSummary.test_name,
                func.sum(TestSummary.count).label("total")
            )
            .where(
                and_(
                    TestSummary.center_id == center.id,
                    TestSummary.date >= since_date
                )
            )
            .group_by(TestSummary.test_code, TestSummary.test_name)
            .order_by(desc("total"))
            .limit(10)
        ).all()

        # Species distribution
        species = self.db.execute(
            select(
                SpeciesSummary.species_name,
                func.sum(SpeciesSummary.count).label("total")
            )
            .where(
                and_(
                    SpeciesSummary.center_id == center.id,
                    SpeciesSummary.date >= since_date
                )
            )
            .group_by(SpeciesSummary.species_name)
            .order_by(desc("total"))
        ).all()

        # Performance metrics (if available)
        perf_metrics = self.db.execute(
            select(
                func.avg(PerformanceMetric.avg_order_processing_time).label("avg_processing"),
                func.avg(PerformanceMetric.completion_rate).label("avg_completion"),
                func.avg(PerformanceMetric.peak_hour).label("typical_peak_hour"),
                func.sum(PerformanceMetric.morning_orders).label("total_morning"),
                func.sum(PerformanceMetric.afternoon_orders).label("total_afternoon"),
                func.sum(PerformanceMetric.evening_orders).label("total_evening"),
                func.sum(PerformanceMetric.night_orders).label("total_night")
            )
            .where(
                and_(
                    PerformanceMetric.center_id == center.id,
                    PerformanceMetric.date >= since_date
                )
            )
        ).one_or_none()

        # Module usage
        modules = self.db.execute(
            select(
                ModuleMetric.module_name,
                func.sum(ModuleMetric.operations_count).label("total_operations"),
                func.avg(ModuleMetric.active_users).label("avg_users"),
                func.sum(ModuleMetric.total_revenue).label("total_revenue")
            )
            .where(
                and_(
                    ModuleMetric.center_id == center.id,
                    ModuleMetric.date >= since_date
                )
            )
            .group_by(ModuleMetric.module_name)
            .order_by(desc("total_operations"))
        ).all()

        # System usage
        system_usage = self.db.execute(
            select(
                func.avg(SystemUsageMetric.total_active_users).label("avg_users"),
                func.max(SystemUsageMetric.peak_concurrent_users).label("max_concurrent"),
                func.avg(SystemUsageMetric.avg_session_duration).label("avg_session"),
                func.sum(SystemUsageMetric.web_access_count).label("total_web"),
                func.sum(SystemUsageMetric.mobile_access_count).label("total_mobile"),
                func.sum(SystemUsageMetric.desktop_access_count).label("total_desktop")
            )
            .where(
                and_(
                    SystemUsageMetric.center_id == center.id,
                    SystemUsageMetric.date >= since_date
                )
            )
        ).one_or_none()

        return {
            "center": {
                "code": center.code,
                "name": center.name,
                "country": center.country,
                "city": center.city,
                "is_active": bool(center.is_active),
                "registered_at": center.registered_at.isoformat() if center.registered_at else None,
                "last_sync_at": center.last_sync_at.isoformat() if center.last_sync_at else None
            },
            "period": {
                "from": since_date.isoformat(),
                "to": date.today().isoformat(),
                "days": days,
                "days_with_data": totals.days_with_data or 0
            },
            "metrics": {
                "total_orders": totals.total_orders or 0,
                "total_results": totals.total_results or 0,
                "total_pets": totals.total_pets or 0,
                "total_owners": totals.total_owners or 0,
                "avg_daily_orders": round(totals.avg_orders, 2) if totals.avg_orders else 0,
                "max_daily_orders": totals.max_orders or 0,
                "min_daily_orders": totals.min_orders or 0
            },
            "top_tests": [
                {
                    "code": t.test_code,
                    "name": t.test_name,
                    "total": t.total
                }
                for t in top_tests
            ],
            "species_distribution": [
                {
                    "species": s.species_name,
                    "total": s.total,
                    "percentage": round((s.total / totals.total_pets * 100), 2) if totals.total_pets else 0
                }
                for s in species
            ],
            "performance": {
                "avg_processing_time_minutes": round(perf_metrics.avg_processing, 2) if perf_metrics and perf_metrics.avg_processing else None,
                "avg_completion_rate": round(perf_metrics.avg_completion, 2) if perf_metrics and perf_metrics.avg_completion else None,
                "typical_peak_hour": round(perf_metrics.typical_peak_hour) if perf_metrics and perf_metrics.typical_peak_hour else None,
                "workload_distribution": {
                    "morning": perf_metrics.total_morning or 0 if perf_metrics else 0,
                    "afternoon": perf_metrics.total_afternoon or 0 if perf_metrics else 0,
                    "evening": perf_metrics.total_evening or 0 if perf_metrics else 0,
                    "night": perf_metrics.total_night or 0 if perf_metrics else 0
                } if perf_metrics else None
            },
            "modules": [
                {
                    "name": m.module_name,
                    "total_operations": m.total_operations,
                    "avg_daily_users": round(m.avg_users, 2) if m.avg_users else 0,
                    "total_revenue_cents": m.total_revenue or 0,
                    "total_revenue_dollars": round((m.total_revenue or 0) / 100, 2)
                }
                for m in modules
            ],
            "system_usage": {
                "avg_daily_users": round(system_usage.avg_users, 2) if system_usage and system_usage.avg_users else None,
                "max_concurrent_users": system_usage.max_concurrent if system_usage else None,
                "avg_session_minutes": round(system_usage.avg_session, 2) if system_usage and system_usage.avg_session else None,
                "access_distribution": {
                    "web": system_usage.total_web or 0 if system_usage else 0,
                    "mobile": system_usage.total_mobile or 0 if system_usage else 0,
                    "desktop": system_usage.total_desktop or 0 if system_usage else 0
                }
            } if system_usage else None
        }

    def compare_centers(self, days: int = 30) -> Dict[str, Any]:
        """
        Compare all centers with rankings and benchmarks

        Returns center comparison with:
        - Total orders ranking
        - Growth rates
        - Efficiency metrics
        - Activity levels
        """
        logger.info(f"Generating centers comparison for last {days} days")

        since_date = date.today() - timedelta(days=days)

        # Get all active centers
        centers = self.db.execute(select(Center)).scalars().all()

        comparison = []
        for center in centers:
            # Metrics for period
            metrics = self.db.execute(
                select(
                    func.sum(DailyMetric.total_orders).label("total_orders"),
                    func.sum(DailyMetric.total_results).label("total_results"),
                    func.sum(DailyMetric.total_pets).label("total_pets"),
                    func.avg(DailyMetric.total_orders).label("avg_daily_orders"),
                    func.count(DailyMetric.id).label("active_days")
                )
                .where(
                    and_(
                        DailyMetric.center_id == center.id,
                        DailyMetric.date >= since_date
                    )
                )
            ).one()

            # Performance metrics
            perf = self.db.execute(
                select(
                    func.avg(PerformanceMetric.completion_rate).label("avg_completion"),
                    func.avg(PerformanceMetric.avg_order_processing_time).label("avg_processing")
                )
                .where(
                    and_(
                        PerformanceMetric.center_id == center.id,
                        PerformanceMetric.date >= since_date
                    )
                )
            ).one_or_none()

            # Calculate growth (compare first half vs second half of period)
            mid_date = since_date + timedelta(days=days // 2)

            first_half = self.db.execute(
                select(func.sum(DailyMetric.total_orders))
                .where(
                    and_(
                        DailyMetric.center_id == center.id,
                        DailyMetric.date >= since_date,
                        DailyMetric.date < mid_date
                    )
                )
            ).scalar() or 0

            second_half = self.db.execute(
                select(func.sum(DailyMetric.total_orders))
                .where(
                    and_(
                        DailyMetric.center_id == center.id,
                        DailyMetric.date >= mid_date
                    )
                )
            ).scalar() or 0

            growth_rate = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0

            comparison.append({
                "center_code": center.code,
                "center_name": center.name,
                "city": center.city,
                "is_active": bool(center.is_active),
                "metrics": {
                    "total_orders": metrics.total_orders or 0,
                    "total_results": metrics.total_results or 0,
                    "total_pets": metrics.total_pets or 0,
                    "avg_daily_orders": round(metrics.avg_daily_orders, 2) if metrics.avg_daily_orders else 0,
                    "active_days": metrics.active_days or 0
                },
                "performance": {
                    "avg_completion_rate": round(perf.avg_completion, 2) if perf and perf.avg_completion else None,
                    "avg_processing_minutes": round(perf.avg_processing, 2) if perf and perf.avg_processing else None
                },
                "growth_rate_percent": round(growth_rate, 2)
            })

        # Sort by total orders
        comparison.sort(key=lambda x: x["metrics"]["total_orders"], reverse=True)

        # Add rankings
        for i, center_data in enumerate(comparison, 1):
            center_data["rank"] = i

        return {
            "period": {
                "from": since_date.isoformat(),
                "to": date.today().isoformat(),
                "days": days
            },
            "total_centers": len(comparison),
            "active_centers": sum(1 for c in comparison if c["is_active"]),
            "centers": comparison,
            "aggregates": {
                "total_orders": sum(c["metrics"]["total_orders"] for c in comparison),
                "total_results": sum(c["metrics"]["total_results"] for c in comparison),
                "total_pets": sum(c["metrics"]["total_pets"] for c in comparison),
                "avg_growth_rate": round(
                    sum(c["growth_rate_percent"] for c in comparison) / len(comparison), 2
                ) if comparison else 0
            }
        }

    def get_center_trends(self, center_code: str, days: int = 30) -> Dict[str, Any]:
        """
        Get daily trends for a center

        Returns time series data for:
        - Daily orders, results, pets
        - Performance metrics
        - Module usage over time
        """
        logger.info(f"Generating trends for center: {center_code}")

        center = self.db.execute(
            select(Center).where(Center.code == center_code)
        ).scalar_one_or_none()

        if not center:
            return None

        since_date = date.today() - timedelta(days=days)

        # Daily metrics trend
        daily_data = self.db.execute(
            select(
                DailyMetric.date,
                DailyMetric.total_orders,
                DailyMetric.total_results,
                DailyMetric.total_pets,
                DailyMetric.total_owners
            )
            .where(
                and_(
                    DailyMetric.center_id == center.id,
                    DailyMetric.date >= since_date
                )
            )
            .order_by(DailyMetric.date)
        ).all()

        return {
            "center": {
                "code": center.code,
                "name": center.name
            },
            "period": {
                "from": since_date.isoformat(),
                "to": date.today().isoformat(),
                "days": days
            },
            "daily_metrics": [
                {
                    "date": d.date.isoformat(),
                    "orders": d.total_orders,
                    "results": d.total_results,
                    "pets": d.total_pets,
                    "owners": d.total_owners
                }
                for d in daily_data
            ]
        }
