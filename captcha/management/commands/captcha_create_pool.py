from django.core.management.base import BaseCommand
from django.db import transaction

from captcha.models import CaptchaStore


class Command(BaseCommand):

    help = "Create a pool of random captchas."

    def add_arguments(self, parser):
        parser.add_argument(
            "--pool-size",
            type=int,
            default=1000,
            help="Number of new captchas to create, default=1000",
        )
        parser.add_argument(
            "--cleanup-expired",
            action="store_true",
            default=True,
            help="Cleanup expired captchas after creating new ones",
        )

    @transaction.atomic()
    def handle(self, **options):
        verbose = int(options.get("verbosity"))
        count = options.get("pool_size")
        CaptchaStore.create_pool(count)
        verbose and self.stdout.write("Created %d new captchas\n" % count)
        options.get("cleanup_expired") and CaptchaStore.remove_expired()
        options.get("cleanup_expired") and verbose and self.stdout.write(
            "Expired captchas cleaned up\n"
        )
