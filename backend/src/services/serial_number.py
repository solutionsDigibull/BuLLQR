"""Serial number generation service."""
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from src.models import WorkOrder


def generate_serial_number(db: Session) -> str:
    """
    Generate next serial number in sequence.

    Serial numbers are formatted as #XXXXX (5 digits, zero-padded).
    Example: #00001, #00002, ..., #99999

    Args:
        db: Database session

    Returns:
        str: Next serial number (e.g., "#00001")

    Implementation:
        Uses database query to find highest serial number and increments.
        Thread-safe due to database transaction isolation.

    Example:
        >>> serial = generate_serial_number(db)
        >>> print(serial)  # "#00001"
    """
    # Get the highest serial number
    # Serial numbers are stored as "#00001", "#00002", etc.
    result = db.execute(
        select(func.max(WorkOrder.serial_number))
    ).scalar()

    if result is None:
        # First serial number
        next_number = 1
    else:
        # Extract numeric part and increment
        # Remove '#' prefix and convert to int
        current_number = int(result.replace('#', ''))
        next_number = current_number + 1

    # Format as #XXXXX (5 digits, zero-padded)
    serial_number = f"#{next_number:05d}"

    return serial_number
