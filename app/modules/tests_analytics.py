# coding: utf-8
"""
Laboratory Tests Analytics Module

Provides comprehensive analytics for laboratory tests including:
- Most requested tests
- Test trends over time
- Test combinations analysis
- Center-specific test patterns
"""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, desc
from loguru import logger

from ..models import Center, TestSummary


class TestsAnalytics:
    """Analytics for laboratory tests"""

    def __init__(self, db: Session):
        self.db = db

    def get_top_tests_global(self, days: int = 30, limit: int = 20) -> Dict[str, Any]:
        """
        Get most requested tests across all centers

        Returns:
            - Test rankings
            - Total counts
            - Growth trends
            - Center distribution
        """
        logger.info(f"Generating global top tests for last {days} days")

        since_date = date.today() - timedelta(days=days)

        # Get top tests
        top_tests = self.db.execute(
            select(
                TestSummary.test_code,
                TestSummary.test_name,
                func.sum(TestSummary.count).label("total_count"),
                func.count(func.distinct(TestSummary.center_id)).label("num_centers"),
                func.avg(TestSummary.count).label("avg_per_day")
            )
            .where(TestSummary.date >= since_date)
            .group_by(TestSummary.test_code, TestSummary.test_name)
            .order_by(desc("total_count"))
            .limit(limit)
        ).all()

        # Calculate growth for each test
        mid_date = since_date + timedelta(days=days // 2)

        tests_with_growth = []
        for test in top_tests:
            # First half
            first_half = self.db.execute(
                select(func.sum(TestSummary.count))
                .where(
                    and_(
                        TestSummary.test_code == test.test_code,
                        TestSummary.date >= since_date,
                        TestSummary.date < mid_date
                    )
                )
            ).scalar() or 0

            # Second half
            second_half = self.db.execute(
                select(func.sum(TestSummary.count))
                .where(
                    and_(
                        TestSummary.test_code == test.test_code,
                        TestSummary.date >= mid_date
                    )
                )
            ).scalar() or 0

            growth = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0

            tests_with_growth.append({
                "code": test.test_code,
                "name": test.test_name or test.test_code,
                "total_count": test.total_count,
                "num_centers": test.num_centers,
                "avg_per_day": round(test.avg_per_day, 2),
                "growth_rate_percent": round(growth, 2)
            })

        return {
            "period": {
                "from": since_date.isoformat(),
                "to": date.today().isoformat(),
                "days": days
            },
            "total_tests": len(tests_with_growth),
            "tests": tests_with_growth
        }

    def get_test_details(self, test_code: str, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed analytics for a specific test

        Returns:
            - Total requests
            - Trend over time
            - Distribution by center
            - Comparison with similar tests
        """
        logger.info(f"Generating details for test: {test_code}")

        since_date = date.today() - timedelta(days=days)

        # Test summary (aggregate all test names for the same code)
        test_info = self.db.execute(
            select(
                TestSummary.test_code,
                func.max(TestSummary.test_name).label("test_name"),  # Take one name
                func.sum(TestSummary.count).label("total_count"),
                func.count(func.distinct(TestSummary.center_id)).label("num_centers"),
                func.max(TestSummary.count).label("max_daily"),
                func.min(TestSummary.count).label("min_daily"),
                func.avg(TestSummary.count).label("avg_daily")
            )
            .where(
                and_(
                    TestSummary.test_code == test_code,
                    TestSummary.date >= since_date
                )
            )
            .group_by(TestSummary.test_code)
        ).one_or_none()

        if not test_info:
            return None

        # Daily trend
        daily_trend = self.db.execute(
            select(
                TestSummary.date,
                func.sum(TestSummary.count).label("total")
            )
            .where(
                and_(
                    TestSummary.test_code == test_code,
                    TestSummary.date >= since_date
                )
            )
            .group_by(TestSummary.date)
            .order_by(TestSummary.date)
        ).all()

        # Distribution by center
        by_center = self.db.execute(
            select(
                Center.code,
                Center.name,
                func.sum(TestSummary.count).label("total")
            )
            .join(TestSummary, Center.id == TestSummary.center_id)
            .where(
                and_(
                    TestSummary.test_code == test_code,
                    TestSummary.date >= since_date
                )
            )
            .group_by(Center.code, Center.name)
            .order_by(desc("total"))
        ).all()

        return {
            "test": {
                "code": test_info.test_code,
                "name": test_info.test_name or test_info.test_code
            },
            "period": {
                "from": since_date.isoformat(),
                "to": date.today().isoformat(),
                "days": days
            },
            "summary": {
                "total_requests": test_info.total_count,
                "num_centers": test_info.num_centers,
                "max_daily": test_info.max_daily,
                "min_daily": test_info.min_daily,
                "avg_daily": round(test_info.avg_daily, 2)
            },
            "daily_trend": [
                {
                    "date": d.date.isoformat(),
                    "count": d.total
                }
                for d in daily_trend
            ],
            "by_center": [
                {
                    "center_code": c.code,
                    "center_name": c.name,
                    "total_requests": c.total,
                    "percentage": round((c.total / test_info.total_count * 100), 2)
                }
                for c in by_center
            ]
        }

    def get_center_tests(self, center_code: str, days: int = 30) -> Dict[str, Any]:
        """
        Get test analytics for a specific center

        Returns:
            - Most requested tests at this center
            - Unique tests (not common in other centers)
            - Test diversity metrics
        """
        logger.info(f"Generating test analytics for center: {center_code}")

        center = self.db.execute(
            select(Center).where(Center.code == center_code)
        ).scalar_one_or_none()

        if not center:
            return None

        since_date = date.today() - timedelta(days=days)

        # Center's top tests
        center_tests = self.db.execute(
            select(
                TestSummary.test_code,
                TestSummary.test_name,
                func.sum(TestSummary.count).label("total_count"),
                func.count(TestSummary.id).label("days_requested"),
                func.avg(TestSummary.count).label("avg_daily")
            )
            .where(
                and_(
                    TestSummary.center_id == center.id,
                    TestSummary.date >= since_date
                )
            )
            .group_by(TestSummary.test_code, TestSummary.test_name)
            .order_by(desc("total_count"))
        ).all()

        # Calculate each test's popularity globally
        tests_with_comparison = []
        for test in center_tests:
            # Global count for this test
            global_count = self.db.execute(
                select(func.sum(TestSummary.count))
                .where(
                    and_(
                        TestSummary.test_code == test.test_code,
                        TestSummary.date >= since_date,
                        TestSummary.center_id != center.id  # Exclude current center
                    )
                )
            ).scalar() or 0

            # Number of other centers using this test
            other_centers = self.db.execute(
                select(func.count(func.distinct(TestSummary.center_id)))
                .where(
                    and_(
                        TestSummary.test_code == test.test_code,
                        TestSummary.date >= since_date,
                        TestSummary.center_id != center.id
                    )
                )
            ).scalar() or 0

            is_unique = other_centers == 0

            tests_with_comparison.append({
                "code": test.test_code,
                "name": test.test_name or test.test_code,
                "total_count": test.total_count,
                "days_requested": test.days_requested,
                "avg_daily": round(test.avg_daily, 2),
                "is_unique_to_center": is_unique,
                "used_by_other_centers": other_centers,
                "global_count": global_count
            })

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
            "summary": {
                "total_different_tests": len(tests_with_comparison),
                "total_test_requests": sum(t["total_count"] for t in tests_with_comparison),
                "unique_tests": sum(1 for t in tests_with_comparison if t["is_unique_to_center"])
            },
            "tests": tests_with_comparison
        }

    def get_test_categories(self, days: int = 30) -> Dict[str, Any]:
        """
        Categorize tests by common patterns in test codes

        Returns categories like:
        - Hematology (CBC, WBC, RBC, etc.)
        - Chemistry (GLU, BUN, CREA, etc.)
        - Enzymes (ALT, AST, ALP, etc.)
        """
        logger.info("Generating test categories analysis")

        since_date = date.today() - timedelta(days=days)

        # Common test categories based on test code patterns
        categories = {
            "Hematology": ["CBC", "WBC", "RBC", "HCT", "HGB", "PLT", "MCV", "MCH", "MCHC"],
            "Chemistry": ["GLU", "BUN", "CREA", "TP", "ALB", "GLOB", "CA", "PHOS", "MG"],
            "Liver_Enzymes": ["ALT", "AST", "ALP", "GGT", "TBIL", "DBIL"],
            "Electrolytes": ["NA", "K", "CL", "CO2", "ANION"],
            "Lipids": ["CHOL", "TRIG", "HDL", "LDL"],
            "Thyroid": ["T4", "T3", "TSH", "FT4"],
            "Hormones": ["CORT", "PROG", "TEST", "ESTRO"],
            "Urinalysis": ["UA", "USG", "UPH", "UPRO", "UGLUC"]
        }

        category_stats = {}
        for category, test_codes in categories.items():
            total = self.db.execute(
                select(func.sum(TestSummary.count))
                .where(
                    and_(
                        TestSummary.test_code.in_(test_codes),
                        TestSummary.date >= since_date
                    )
                )
            ).scalar() or 0

            if total > 0:
                category_stats[category] = total

        # Sort by total
        sorted_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)

        total_all = sum(category_stats.values())

        return {
            "period": {
                "from": since_date.isoformat(),
                "to": date.today().isoformat(),
                "days": days
            },
            "total_categorized_tests": total_all,
            "categories": [
                {
                    "name": cat,
                    "total_requests": count,
                    "percentage": round((count / total_all * 100), 2) if total_all > 0 else 0
                }
                for cat, count in sorted_categories
            ]
        }
