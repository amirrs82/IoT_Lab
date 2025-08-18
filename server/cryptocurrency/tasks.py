from celery import shared_task
from django.utils import timezone
from cryptocurrency.models import Currency
from cryptocurrency.scripts import get_current_price_and_daily_change, get_multiple_currencies_prices
import logging

logger = logging.getLogger(__name__)


@shared_task
def update_currency_prices():
    """
    Celery task to update all currency prices and daily change percentages
    Uses batch API calls to avoid rate limiting
    """
    logger.info("Starting currency price update task")
    
    currencies = Currency.objects.all()
    updated_count = 0
    error_count = 0
    
    # Get all coin IDs for batch processing
    coin_ids = [currency.key for currency in currencies]
    
    if not coin_ids:
        logger.info("No currencies found to update")
        return {'updated_count': 0, 'error_count': 0, 'total_currencies': 0}
    
    # Get prices for all currencies in batch
    logger.info(f"Fetching prices for {len(coin_ids)} currencies in batch")
    price_results = get_multiple_currencies_prices(coin_ids)
    
    # Update each currency with the results
    for currency in currencies:
        try:
            result = price_results.get(currency.key)
            
            if result and 'error' not in result and result.get('price') is not None:
                # Update currency with new price data
                currency.last_price = result['price']
                currency.last_day_change = result['change_percentage']
                currency.last_price_update = timezone.now()
                currency.save()
                
                updated_count += 1
                logger.info(f"Updated {currency.name} ({currency.key}): ${result['price']}, {result.get('change_percentage', 0):.2f}%")
            else:
                error_msg = result.get('error', 'No data returned') if result else 'No result found'
                logger.error(f"Failed to update {currency.name} ({currency.key}): {error_msg}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"Exception updating {currency.name} ({currency.key}): {str(e)}")
            error_count += 1
    
    logger.info(f"Currency price update completed. Updated: {updated_count}, Errors: {error_count}")
    return {
        'updated_count': updated_count,
        'error_count': error_count,
        'total_currencies': currencies.count()
    }
