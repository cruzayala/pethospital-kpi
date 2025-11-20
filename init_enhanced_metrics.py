# coding: utf-8
"""
Initialize enhanced metrics tables in the database (v2.1)

This script creates the new intelligent metrics tables if they don't exist.
Safe to run multiple times (uses IF NOT EXISTS).
"""
import sys
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

def init_enhanced_metrics():
    """Create enhanced metrics tables"""
    from app.database import engine
    from app.models import (
        Base, PerformanceMetric, ModuleMetric,
        SystemUsageMetric, PaymentMethodMetric
    )

    logger.info("Initializing enhanced metrics tables (v2.1)...")

    try:
        # Create all tables (only creates missing ones)
        Base.metadata.create_all(bind=engine)

        logger.success("Enhanced metrics tables initialized successfully!")
        logger.info("New tables created:")
        logger.info("  - performance_metrics")
        logger.info("  - module_metrics")
        logger.info("  - system_usage_metrics")
        logger.info("  - payment_method_metrics")

        return True

    except Exception as e:
        logger.error(f"Failed to initialize enhanced metrics tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("PETHOSPITAL KPI SERVICE - Enhanced Metrics Initialization v2.1")
    logger.info("=" * 70)

    success = init_enhanced_metrics()

    if success:
        logger.info("\n" + "=" * 70)
        logger.success("INITIALIZATION COMPLETE!")
        logger.info("=" * 70)
        logger.info("\nYou can now use the enhanced metrics endpoints:")
        logger.info("  - POST /kpi/submit/enhanced")
        logger.info("\nEnhanced metrics include:")
        logger.info("  - Performance metrics (processing times, peak hours)")
        logger.info("  - Module usage (laboratorio, consultas, farmacia, etc.)")
        logger.info("  - System usage (users, sessions, access types)")
        logger.info("  - Payment methods (efectivo, tarjeta, transferencia, etc.)")
        sys.exit(0)
    else:
        logger.error("\nInitialization failed. Please check the error messages above.")
        sys.exit(1)
