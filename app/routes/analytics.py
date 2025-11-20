# coding: utf-8
"""
Analytics API Routes

Provides comprehensive analytics endpoints using specialized modules:
- Centers analytics
- Tests analytics
- Species & breeds analytics
- Performance analytics
"""
from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from loguru import logger

from ..database import get_db
from ..modules.centers_analytics import CentersAnalytics
from ..modules.tests_analytics import TestsAnalytics
from ..modules.species_analytics import SpeciesAnalytics
from ..modules.export_service import ExportService
from ..modules.cache_service import get_cache_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ============================================================================
# CENTERS ANALYTICS
# ============================================================================

@router.get("/centers/summary/{center_code}")
def get_center_summary(
    center_code: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive summary for a specific center

    Includes:
    - Basic metrics (orders, results, pets, owners)
    - Top tests
    - Species distribution
    - Performance indicators
    - Module usage
    - System usage

    Public endpoint (no authentication required)
    """
    logger.info(f"Center summary requested: {center_code}")

    analytics = CentersAnalytics(db)
    result = analytics.get_center_summary(center_code, days)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Center {center_code} not found"
        )

    return result


@router.get("/centers/comparison")
def compare_centers(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Compare all centers with rankings and benchmarks

    Returns:
    - Center rankings by total orders
    - Growth rates
    - Performance comparisons
    - Activity levels

    Public endpoint (no authentication required)
    """
    logger.info("Centers comparison requested")

    analytics = CentersAnalytics(db)
    return analytics.compare_centers(days)


@router.get("/centers/trends/{center_code}")
def get_center_trends(
    center_code: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get daily trends for a center

    Returns time series data for:
    - Daily orders, results, pets, owners
    - Performance metrics
    - Module usage over time

    Public endpoint (no authentication required)
    """
    logger.info(f"Center trends requested: {center_code}")

    analytics = CentersAnalytics(db)
    result = analytics.get_center_trends(center_code, days)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Center {center_code} not found"
        )

    return result


# ============================================================================
# TESTS ANALYTICS
# ============================================================================

@router.get("/tests/top-global")
def get_top_tests_global(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(20, ge=1, le=100, description="Number of tests to return"),
    db: Session = Depends(get_db)
):
    """
    Get most requested tests across all centers

    Returns:
    - Test rankings
    - Total counts
    - Growth trends
    - Center distribution

    Public endpoint (no authentication required)
    """
    logger.info(f"Top tests global requested (limit={limit})")

    analytics = TestsAnalytics(db)
    return analytics.get_top_tests_global(days, limit)


@router.get("/tests/details/{test_code}")
def get_test_details(
    test_code: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a specific test

    Returns:
    - Total requests
    - Trend over time
    - Distribution by center
    - Comparison metrics

    Public endpoint (no authentication required)
    """
    logger.info(f"Test details requested: {test_code}")

    analytics = TestsAnalytics(db)
    result = analytics.get_test_details(test_code, days)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test {test_code} not found in the specified period"
        )

    return result


@router.get("/tests/by-center/{center_code}")
def get_center_tests(
    center_code: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get test analytics for a specific center

    Returns:
    - Most requested tests at this center
    - Unique tests (not common in other centers)
    - Test diversity metrics

    Public endpoint (no authentication required)
    """
    logger.info(f"Center tests requested: {center_code}")

    analytics = TestsAnalytics(db)
    result = analytics.get_center_tests(center_code, days)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Center {center_code} not found"
        )

    return result


@router.get("/tests/categories")
def get_test_categories(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get test categories analysis

    Categorizes tests by common patterns:
    - Hematology (CBC, WBC, RBC, etc.)
    - Chemistry (GLU, BUN, CREA, etc.)
    - Liver Enzymes (ALT, AST, ALP, etc.)
    - Electrolytes, Lipids, Thyroid, etc.

    Public endpoint (no authentication required)
    """
    logger.info("Test categories requested")

    analytics = TestsAnalytics(db)
    return analytics.get_test_categories(days)


# ============================================================================
# SPECIES & BREEDS ANALYTICS
# ============================================================================

@router.get("/species/distribution")
def get_species_distribution(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get global species distribution

    Returns:
    - Species counts and percentages
    - Trend over time
    - Distribution by center

    Public endpoint (no authentication required)
    """
    logger.info("Species distribution requested")

    analytics = SpeciesAnalytics(db)
    return analytics.get_species_distribution(days)


@router.get("/breeds/top")
def get_top_breeds(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(20, ge=1, le=100, description="Number of breeds to return"),
    species: Optional[str] = Query(None, description="Filter by species"),
    db: Session = Depends(get_db)
):
    """
    Get most common breeds globally or for a specific species

    Returns:
    - Breed rankings
    - Species breakdown
    - Popularity trends

    Public endpoint (no authentication required)
    """
    logger.info(f"Top breeds requested (species={species}, limit={limit})")

    analytics = SpeciesAnalytics(db)
    return analytics.get_top_breeds(days, limit, species)


@router.get("/species/by-center/{center_code}")
def get_center_species_profile(
    center_code: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get species and breed profile for a specific center

    Returns:
    - Species distribution at this center
    - Most common breeds
    - Comparison with global patterns

    Public endpoint (no authentication required)
    """
    logger.info(f"Center species profile requested: {center_code}")

    analytics = SpeciesAnalytics(db)
    result = analytics.get_center_species_profile(center_code, days)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Center {center_code} not found"
        )

    return result


@router.get("/breeds/details/{breed_name}")
def get_breed_details(
    breed_name: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a specific breed

    Returns:
    - Total count across centers
    - Geographic distribution
    - Trend over time

    Public endpoint (no authentication required)
    """
    logger.info(f"Breed details requested: {breed_name}")

    analytics = SpeciesAnalytics(db)
    result = analytics.get_breed_details(breed_name, days)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Breed {breed_name} not found in the specified period"
        )

    return result


# ============================================================================
# QUICK SUMMARY (ALL-IN-ONE)
# ============================================================================

@router.get("/summary")
def get_global_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive global summary (all analytics in one call)

    Returns:
    - Centers comparison
    - Top tests
    - Species distribution
    - Top breeds

    Public endpoint (no authentication required)
    Useful for dashboard overview
    """
    logger.info("Global summary requested")

    centers_analytics = CentersAnalytics(db)
    tests_analytics = TestsAnalytics(db)
    species_analytics = SpeciesAnalytics(db)

    return {
        "period": {
            "days": days
        },
        "centers": centers_analytics.compare_centers(days),
        "top_tests": tests_analytics.get_top_tests_global(days, limit=10),
        "species": species_analytics.get_species_distribution(days),
        "top_breeds": species_analytics.get_top_breeds(days, limit=10)
    }


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@router.get("/export/centers/comparison")
def export_centers_comparison(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    format: str = Query("csv", regex="^(csv|excel|pdf)$", description="Export format"),
    db: Session = Depends(get_db)
):
    """
    Export centers comparison data

    Formats:
    - csv: CSV file for spreadsheet import
    - excel: Excel file with formatting
    - pdf: PDF report with tables and summary

    Public endpoint (no authentication required)
    """
    logger.info(f"Export centers comparison requested: format={format}")

    analytics = CentersAnalytics(db)
    data = analytics.compare_centers(days)

    # Generate export
    export_buffer = ExportService.export_centers_comparison(data, format)

    # Determine content type and filename
    content_types = {
        "csv": "text/csv",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf"
    }
    extensions = {
        "csv": "csv",
        "excel": "xlsx",
        "pdf": "pdf"
    }

    filename = f"centros_comparacion_{date.today().isoformat()}.{extensions[format]}"

    return StreamingResponse(
        export_buffer,
        media_type=content_types[format],
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/tests/top")
def export_top_tests(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(20, ge=1, le=100, description="Number of tests to export"),
    format: str = Query("csv", regex="^(csv|excel|pdf)$", description="Export format"),
    db: Session = Depends(get_db)
):
    """
    Export top tests data

    Formats:
    - csv: CSV file for spreadsheet import
    - excel: Excel file with formatting
    - pdf: PDF report with tables and summary

    Public endpoint (no authentication required)
    """
    logger.info(f"Export top tests requested: format={format}, limit={limit}")

    analytics = TestsAnalytics(db)
    data = analytics.get_top_tests_global(days, limit)

    # Generate export
    export_buffer = ExportService.export_top_tests(data, format)

    # Determine content type and filename
    content_types = {
        "csv": "text/csv",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf"
    }
    extensions = {
        "csv": "csv",
        "excel": "xlsx",
        "pdf": "pdf"
    }

    filename = f"top_pruebas_{date.today().isoformat()}.{extensions[format]}"

    return StreamingResponse(
        export_buffer,
        media_type=content_types[format],
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ============================================================================
# ADVANCED FILTERS (DATE RANGE)
# ============================================================================

@router.get("/centers/comparison/advanced")
def compare_centers_advanced(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Number of days (alternative to dates)"),
    db: Session = Depends(get_db)
):
    """
    Compare centers with advanced date filtering

    You can either:
    - Specify start_date and end_date (YYYY-MM-DD format)
    - Specify days (will calculate from today backwards)

    Public endpoint (no authentication required)
    """
    logger.info(f"Advanced centers comparison: start={start_date}, end={end_date}, days={days}")

    # Calculate date range
    if start_date and end_date:
        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
            calculated_days = (end - start).days
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    elif days:
        calculated_days = days
    else:
        calculated_days = 30  # Default

    analytics = CentersAnalytics(db)
    return analytics.compare_centers(calculated_days)


@router.get("/tests/top-global/advanced")
def get_top_tests_advanced(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Number of days"),
    limit: int = Query(20, ge=1, le=100, description="Number of tests to return"),
    db: Session = Depends(get_db)
):
    """
    Get top tests with advanced date filtering

    You can either:
    - Specify start_date and end_date (YYYY-MM-DD format)
    - Specify days (will calculate from today backwards)

    Public endpoint (no authentication required)
    """
    logger.info(f"Advanced top tests: start={start_date}, end={end_date}, days={days}")

    # Calculate date range
    if start_date and end_date:
        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
            calculated_days = (end - start).days
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    elif days:
        calculated_days = days
    else:
        calculated_days = 30  # Default

    analytics = TestsAnalytics(db)
    return analytics.get_top_tests_global(calculated_days, limit)


# ============================================================================
# CACHE STATS
# ============================================================================

@router.get("/cache/stats")
def get_cache_stats():
    """
    Get cache statistics

    Returns hit rate, total keys, etc.
    Useful for monitoring cache performance

    Public endpoint (no authentication required)
    """
    logger.info("Cache stats requested")

    cache = get_cache_service()
    if not cache:
        return {
            "enabled": False,
            "message": "Cache service not initialized"
        }

    return cache.get_stats()


@router.post("/cache/clear")
def clear_cache(
    pattern: str = Query("analytics:*", description="Key pattern to clear")
):
    """
    Clear cache keys matching pattern

    Patterns:
    - analytics:* - All analytics cache
    - analytics:centers:* - Only centers cache
    - analytics:tests:* - Only tests cache

    Public endpoint (no authentication required)
    Note: In production, this should require admin authentication
    """
    logger.info(f"Cache clear requested: pattern={pattern}")

    cache = get_cache_service()
    if not cache:
        return {
            "success": False,
            "message": "Cache service not initialized"
        }

    count = cache.clear_pattern(pattern)
    return {
        "success": True,
        "keys_cleared": count,
        "pattern": pattern
    }
