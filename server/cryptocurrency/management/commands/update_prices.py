from django.core.management.base import BaseCommand
from cryptocurrency.tasks import update_currency_prices


class Command(BaseCommand):
    help = 'Manually update currency prices'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting currency price update...'))
        result = update_currency_prices()
        self.stdout.write(
            self.style.SUCCESS(
                f'Update completed. Updated: {result["updated_count"]}, '
                f'Errors: {result["error_count"]}, '
                f'Total: {result["total_currencies"]}'
            )
        )
