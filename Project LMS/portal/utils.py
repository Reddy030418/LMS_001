from django.utils import timezone
from decimal import Decimal

FINE_PER_DAY = Decimal('2.00')

def calculate_fine(due_date, returned_date=None):
    if returned_date is None:
        returned_date = timezone.localdate()
    delay = (returned_date - due_date).days
    if delay > 0:
        return FINE_PER_DAY * delay
    return Decimal('0.00')
