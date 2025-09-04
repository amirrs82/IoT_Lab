from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from cryptocurrency.models import Currency


class Command(BaseCommand):
    help = 'Add popular cryptocurrencies to the database'

    def handle(self, *args, **options):
        # Popular cryptocurrencies with their CoinGecko IDs
        popular_currencies = [
            {"name": "Bitcoin", "key": "bitcoin"},
            {"name": "Tether", "key": "tether"},
            {"name": "Ethereum", "key": "ethereum"},
            {"name": "Toncoin", "key": "the-open-network"},
            {"name": "Solana", "key": "solana"},
            {"name": "TRON", "key": "tron"},
            {"name": "BNB", "key": "binancecoin"},
            {"name": "XRP", "key": "ripple"},
            {"name": "Dogecoin", "key": "dogecoin"},
            {"name": "Cardano", "key": "cardano"},
            {"name": "Avalanche", "key": "avalanche-2"},
            {"name": "Polygon", "key": "matic-network"},
            {"name": "Chainlink", "key": "chainlink"},
            {"name": "Polkadot", "key": "polkadot"},
            {"name": "Litecoin", "key": "litecoin"},
            {"name": "Shiba Inu", "key": "shiba-inu"},
            {"name": "NEAR Protocol", "key": "near"},
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for currency_data in popular_currencies:
            try:
                with transaction.atomic():
                    currency, created = Currency.objects.get_or_create(
                        key=currency_data["key"],
                        defaults={"name": currency_data["name"]}
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Created: {currency.name} ({currency.key})')
                        )
                    else:
                        # Update name if it exists but name is different
                        if currency.name != currency_data["name"]:
                            currency.name = currency_data["name"]
                            currency.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'🔄 Updated: {currency.name} ({currency.key})')
                            )
                        else:
                            skipped_count += 1
                            self.stdout.write(
                                self.style.HTTP_INFO(f'ℹ️  Already exists: {currency.name} ({currency.key})')
                            )
            except IntegrityError as e:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Skipped {currency_data["name"]} ({currency_data["key"]}) - IntegrityError: {str(e)}'
                    )
                )
            except Exception as e:
                skipped_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error processing {currency_data["name"]} ({currency_data["key"]}): {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 Summary: {created_count} created, {updated_count} updated, {skipped_count} skipped'
            )
        )
