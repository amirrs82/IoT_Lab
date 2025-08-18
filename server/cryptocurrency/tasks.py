from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from cryptocurrency.models import Currency, CurrencySubscription
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
                
                # Check for subscription alerts after price update
                check_subscription_alerts.delay(currency.uuid, result['price'])
                
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


@shared_task
def check_subscription_alerts(currency_uuid, new_price):
    """
    Celery task to check for subscription alerts after currency price update
    Sends email notifications when price thresholds are met
    """
    logger.info(f"Checking subscription alerts for currency {currency_uuid} with new price {new_price}")
    
    try:
        # Get the currency object
        currency = Currency.objects.get(uuid=currency_uuid)
        
        # Get all WAITING subscriptions for this currency
        waiting_subscriptions = CurrencySubscription.objects.filter(
            currency=currency,
            status=CurrencySubscription.StatusChoices.WAITING
        )
        
        alerts_sent = 0
        alerts_failed = 0
        
        for subscription in waiting_subscriptions:
            try:
                # Check if alert condition is met
                alert_triggered = False
                alert_type = ""
                threshold_value = None
                
                if subscription.floor is not None and new_price <= subscription.floor:
                    alert_triggered = True
                    alert_type = "floor"
                    threshold_value = subscription.floor
                elif subscription.ceiling is not None and new_price >= subscription.ceiling:
                    alert_triggered = True
                    alert_type = "ceiling"
                    threshold_value = subscription.ceiling
                
                if alert_triggered:
                    # Send email notification
                    success = send_price_alert_email(
                        subscription.user,
                        currency,
                        new_price,
                        alert_type,
                        threshold_value
                    )
                    
                    if success:
                        # Mark subscription as DONE
                        subscription.status = CurrencySubscription.StatusChoices.DONE
                        subscription.save()
                        alerts_sent += 1
                        logger.info(f"Alert sent successfully for {subscription.user.username} - {currency.name} ({alert_type}: {threshold_value})")
                    else:
                        alerts_failed += 1
                        logger.error(f"Failed to send alert for {subscription.user.username} - {currency.name}")
                        
            except Exception as e:
                alerts_failed += 1
                logger.error(f"Error processing subscription {subscription.uuid}: {str(e)}")
        
        logger.info(f"Subscription alerts completed. Sent: {alerts_sent}, Failed: {alerts_failed}")
        return {
            'currency': str(currency_uuid),
            'new_price': float(new_price),
            'alerts_sent': alerts_sent,
            'alerts_failed': alerts_failed
        }
        
    except Currency.DoesNotExist:
        logger.error(f"Currency with UUID {currency_uuid} not found")
        return {'error': 'Currency not found'}
    except Exception as e:
        logger.error(f"Error in check_subscription_alerts: {str(e)}")
        return {'error': str(e)}


def send_price_alert_email(user, currency, new_price, alert_type, threshold_value):
    """
    Send price alert email to user
    Returns True if email sent successfully, False otherwise
    """
    try:
        # Prepare email content
        if alert_type == "floor":
            subject = f"Price Alert: {currency.name} Dropped Below Your Floor Price"
            message = (
                f"Hi {user.first_name or user.username},\n\n"
                f"Your price alert for {currency.name} ({currency.key}) has been triggered!\n\n"
                f"• Floor price you set: ${threshold_value}\n"
                f"• Current price: ${new_price}\n\n"
                f"The price has dropped below your floor threshold.\n\n"
                f"Best regards,\n"
                f"IoT Lab Crypto Team"
            )
        else:  # ceiling
            subject = f"Price Alert: {currency.name} Rose Above Your Ceiling Price"
            message = (
                f"Hi {user.first_name or user.username},\n\n"
                f"Your price alert for {currency.name} ({currency.key}) has been triggered!\n\n"
                f"• Ceiling price you set: ${threshold_value}\n"
                f"• Current price: ${new_price}\n\n"
                f"The price has risen above your ceiling threshold.\n\n"
                f"Best regards,\n"
                f"IoT Lab Crypto Team"
            )
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        
        # Send the email
        send_mail(subject, message, from_email, recipient_list)
        return True
        
    except Exception as e:
        logger.error(f"Failed to send price alert email to {user.email}: {str(e)}")
        return False
