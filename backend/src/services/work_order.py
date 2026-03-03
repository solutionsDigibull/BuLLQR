"""Work order service for lookup and creation."""
from sqlalchemy.orm import Session
from src.models import WorkOrder, Product
from datetime import datetime
import uuid


def get_or_create_work_order(db: Session, barcode: str) -> WorkOrder:
    """
    Get existing work order by barcode or create new one.

    Args:
        db: Database session
        barcode: Work order barcode (20-50 characters)

    Returns:
        WorkOrder: Existing or newly created work order

    Raises:
        ValueError: If no active product configured

    Example:
        >>> work_order = get_or_create_work_order(db, "TREO-TRAND-12345-001")
        >>> print(work_order.work_order_code)  # "TREO-TRAND-12345-001"
    """
    # Try to find existing work order
    work_order = db.query(WorkOrder).filter(WorkOrder.work_order_code == barcode).first()

    if work_order:
        return work_order

    # Create new work order
    # Get active product
    active_product = db.query(Product).filter(Product.is_active == True).first()
    if not active_product:
        raise ValueError("No active product configured. Please set an active product first.")

    # Generate next serial number (integer)
    from src.services.serial_number import generate_serial_number
    serial_number = generate_serial_number(db)

    # Create work order
    work_order = WorkOrder(
        id=uuid.uuid4(),
        work_order_code=barcode,
        product_id=active_product.id,
        serial_number=serial_number,
        current_stage_id=None,
        is_completed=False,
        overall_quality_status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(work_order)
    db.flush()  # Flush to get ID without committing

    return work_order
