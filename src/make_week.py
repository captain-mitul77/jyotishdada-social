"""Pre-generate the next N days (default 7) so you can bulk-upload and SCHEDULE them in the native apps
(YouTube Studio, Instagram, Facebook Meta Business Suite) instead of using the API.
Panchang values are pure functions of city + date, so future days are exactly what that day will show.

    DAYS=7 python src/make_week.py      -> out/<date>/ for each of the next 7 days (starting tomorrow IST)
"""
import datetime as dt
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data  # noqa: E402
import make_posts  # noqa: E402

if __name__ == "__main__":
    start = data.today_ist() + dt.timedelta(days=1)
    for i in range(int(os.environ.get("DAYS", "7"))):
        os.environ["POST_DATE"] = (start + dt.timedelta(days=i)).isoformat()
        make_posts.main()
