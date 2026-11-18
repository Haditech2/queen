"""Build step used by Vercel.

Vercel detects the Django project from ``manage.py`` and automatically runs
``collectstatic`` for us, so this script only handles the database:

1. apply migrations
2. seed the verified Nigerian crisis resources / coping tools / admin user

Migrations + seeding are skipped when no PostgreSQL ``DATABASE_URL`` is
available (for example on a brand-new deploy where the database has not been
attached yet), so the first build never fails because of a missing database.
"""

import os
import subprocess
import sys


def run(*args):
    print(f"$ {' '.join(args)}", flush=True)
    subprocess.run(args, check=True)


def main():
    database_url = os.environ.get("DATABASE_URL", "")

    if not database_url.startswith(("postgres://", "postgresql://")):
        print(
            "\n[build] No PostgreSQL DATABASE_URL found.\n"
            "[build] Skipping migrations and seeding.\n"
            "[build] Add a PostgreSQL database (Neon/Supabase) in the Vercel\n"
            "[build] dashboard so DATABASE_URL is injected, then redeploy.\n",
            flush=True,
        )
        return

    run(sys.executable, "manage.py", "migrate", "--noinput")
    run(sys.executable, "manage.py", "seed_data")


if __name__ == "__main__":
    main()
