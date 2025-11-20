# coding: utf-8
"""
Species and Breeds Analytics Module

Provides comprehensive analytics for species and breeds including:
- Species distribution
- Most common breeds
- Breed trends
- Cross-species comparisons
"""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, desc
from loguru import logger

from ..models import Center, SpeciesSummary, BreedSummary


class SpeciesAnalytics:
    """Analytics for species and breeds"""

    def __init__(self, db: Session):
        self.db = db

    def get_species_distribution(self, days: int = 30) -> Dict[str, Any]:
        """
        Get global species distribution

        Returns:
            - Species counts and percentages
            - Trend over time
            - Distribution by center
        """
        logger.info(f"Generating species distribution for last {days} days")

        since_date = date.today() - timedelta(days=days)

        # Global species distribution
        species_data = self.db.execute(
            select(
                SpeciesSummary.species_name,
                func.sum(SpeciesSummary.count).label("total_count"),
                func.count(func.distinct(SpeciesSummary.center_id)).label("num_centers"),
                func.avg(SpeciesSummary.count).label("avg_per_day")
            )
            .where(SpeciesSummary.date >= since_date)
            .group_by(SpeciesSummary.species_name)
            .order_by(desc("total_count"))
        ).all()

        total_animals = sum(s.total_count for s in species_data)

        # Daily trend for top species
        top_species = [s.species_name for s in species_data[:3]]  # Top 3
        daily_trends = {}

        for species_name in top_species:
            trend = self.db.execute(
                select(
                    SpeciesSummary.date,
                    func.sum(SpeciesSummary.count).label("total")
                )
                .where(
                    and_(
                        SpeciesSummary.species_name == species_name,
                        SpeciesSummary.date >= since_date
                    )
                )
                .group_by(SpeciesSummary.date)
                .order_by(SpeciesSummary.date)
            ).all()

            daily_trends[species_name] = [
                {"date": d.date.isoformat(), "count": d.total}
                for d in trend
            ]

        return {
            "period": {
                "from": since_date.isoformat(),
                "to": date.today().isoformat(),
                "days": days
            },
            "summary": {
                "total_animals": total_animals,
                "num_species": len(species_data)
            },
            "species": [
                {
                    "name": s.species_name,
                    "total_count": s.total_count,
                    "percentage": round((s.total_count / total_animals * 100), 2) if total_animals > 0 else 0,
                    "num_centers": s.num_centers,
                    "avg_per_day": round(s.avg_per_day, 2)
                }
                for s in species_data
            ],
            "daily_trends": daily_trends
        }

    def get_top_breeds(self, days: int = 30, limit: int = 20, species: Optional[str] = None) -> Dict[str, Any]:
        """
        Get most common breeds globally or for a specific species

        Returns:
            - Breed rankings
            - Species breakdown
            - Popularity trends
        """
        logger.info(f"Generating top breeds analysis (species={species})")

        since_date = date.today() - timedelta(days=days)

        # Build query
        query = select(
            BreedSummary.breed_name,
            BreedSummary.species_name,
            func.sum(BreedSummary.count).label("total_count"),
            func.count(func.distinct(BreedSummary.center_id)).label("num_centers"),
            func.avg(BreedSummary.count).label("avg_per_day")
        ).where(BreedSummary.date >= since_date)

        if species:
            query = query.where(BreedSummary.species_name == species)

        breeds_data = self.db.execute(
            query.group_by(BreedSummary.breed_name, BreedSummary.species_name)
            .order_by(desc("total_count"))
            .limit(limit)
        ).all()

        total_breeds = self.db.execute(
            select(func.count(func.distinct(BreedSummary.breed_name)))
            .where(BreedSummary.date >= since_date)
        ).scalar()

        return {
            "period": {
                "from": since_date.isoformat(),
                "to": date.today().isoformat(),
                "days": days
            },
            "filter": {
                "species": species if species else "all"
            },
            "summary": {
                "total_different_breeds": total_breeds,
                "showing_top": len(breeds_data)
            },
            "breeds": [
                {
                    "breed": b.breed_name,
                    "species": b.species_name,
                    "total_count": b.total_count,
                    "num_centers": b.num_centers,
                    "avg_per_day": round(b.avg_per_day, 2)
                }
                for b in breeds_data
            ]
        }

    def get_center_species_profile(self, center_code: str, days: int = 30) -> Dict[str, Any]:
        """
        Get species and breed profile for a specific center

        Returns:
            - Species distribution at this center
            - Most common breeds
            - Comparison with global patterns
        """
        logger.info(f"Generating species profile for center: {center_code}")

        center = self.db.execute(
            select(Center).where(Center.code == center_code)
        ).scalar_one_or_none()

        if not center:
            return None

        since_date = date.today() - timedelta(days=days)

        # Center's species distribution
        center_species = self.db.execute(
            select(
                SpeciesSummary.species_name,
                func.sum(SpeciesSummary.count).label("total_count")
            )
            .where(
                and_(
                    SpeciesSummary.center_id == center.id,
                    SpeciesSummary.date >= since_date
                )
            )
            .group_by(SpeciesSummary.species_name)
            .order_by(desc("total_count"))
        ).all()

        total_center = sum(s.total_count for s in center_species)

        # Global species distribution for comparison
        global_species = self.db.execute(
            select(
                SpeciesSummary.species_name,
                func.sum(SpeciesSummary.count).label("total_count")
            )
            .where(SpeciesSummary.date >= since_date)
            .group_by(SpeciesSummary.species_name)
        ).all()

        total_global = sum(s.total_count for s in global_species)
        global_percentages = {s.species_name: (s.total_count / total_global * 100) for s in global_species}

        # Center's top breeds
        center_breeds = self.db.execute(
            select(
                BreedSummary.breed_name,
                BreedSummary.species_name,
                func.sum(BreedSummary.count).label("total_count")
            )
            .where(
                and_(
                    BreedSummary.center_id == center.id,
                    BreedSummary.date >= since_date
                )
            )
            .group_by(BreedSummary.breed_name, BreedSummary.species_name)
            .order_by(desc("total_count"))
            .limit(10)
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
            "species": [
                {
                    "name": s.species_name,
                    "count": s.total_count,
                    "percentage_at_center": round((s.total_count / total_center * 100), 2) if total_center > 0 else 0,
                    "percentage_globally": round(global_percentages.get(s.species_name, 0), 2),
                    "difference": round((s.total_count / total_center * 100 - global_percentages.get(s.species_name, 0)), 2) if total_center > 0 else 0
                }
                for s in center_species
            ],
            "top_breeds": [
                {
                    "breed": b.breed_name,
                    "species": b.species_name,
                    "count": b.total_count
                }
                for b in center_breeds
            ]
        }

    def get_breed_details(self, breed_name: str, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed analytics for a specific breed

        Returns:
            - Total count across centers
            - Geographic distribution
            - Trend over time
        """
        logger.info(f"Generating details for breed: {breed_name}")

        since_date = date.today() - timedelta(days=days)

        # Breed summary
        breed_info = self.db.execute(
            select(
                BreedSummary.breed_name,
                BreedSummary.species_name,
                func.sum(BreedSummary.count).label("total_count"),
                func.count(func.distinct(BreedSummary.center_id)).label("num_centers"),
                func.avg(BreedSummary.count).label("avg_per_day")
            )
            .where(
                and_(
                    BreedSummary.breed_name == breed_name,
                    BreedSummary.date >= since_date
                )
            )
            .group_by(BreedSummary.breed_name, BreedSummary.species_name)
        ).one_or_none()

        if not breed_info:
            return None

        # Distribution by center
        by_center = self.db.execute(
            select(
                Center.code,
                Center.name,
                Center.city,
                func.sum(BreedSummary.count).label("total")
            )
            .join(BreedSummary, Center.id == BreedSummary.center_id)
            .where(
                and_(
                    BreedSummary.breed_name == breed_name,
                    BreedSummary.date >= since_date
                )
            )
            .group_by(Center.code, Center.name, Center.city)
            .order_by(desc("total"))
        ).all()

        # Daily trend
        daily_trend = self.db.execute(
            select(
                BreedSummary.date,
                func.sum(BreedSummary.count).label("total")
            )
            .where(
                and_(
                    BreedSummary.breed_name == breed_name,
                    BreedSummary.date >= since_date
                )
            )
            .group_by(BreedSummary.date)
            .order_by(BreedSummary.date)
        ).all()

        return {
            "breed": {
                "name": breed_info.breed_name,
                "species": breed_info.species_name
            },
            "period": {
                "from": since_date.isoformat(),
                "to": date.today().isoformat(),
                "days": days
            },
            "summary": {
                "total_count": breed_info.total_count,
                "num_centers": breed_info.num_centers,
                "avg_per_day": round(breed_info.avg_per_day, 2)
            },
            "by_center": [
                {
                    "center_code": c.code,
                    "center_name": c.name,
                    "city": c.city,
                    "count": c.total,
                    "percentage": round((c.total / breed_info.total_count * 100), 2)
                }
                for c in by_center
            ],
            "daily_trend": [
                {"date": d.date.isoformat(), "count": d.total}
                for d in daily_trend
            ]
        }
