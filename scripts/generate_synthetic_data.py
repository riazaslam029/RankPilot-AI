import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

np.random.seed(42)

PAGES = 2000
SITES = ["exampledomain.com", "testsite.io", "demoapp.co"]
DAYS = 180
START_DATE = datetime(2025, 1, 1)


def main():
    out_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {PAGES} pages over {DAYS} days...")

    records = []
    for i in range(PAGES):
        page = f"/page-{i:05d}"
        site = np.random.choice(SITES)
        base_ctr = np.random.lognormal(mean=-2.5, sigma=0.8)
        base_position = np.random.lognormal(mean=3.0, sigma=1.2)
        base_impressions = np.random.lognormal(mean=8.0, sigma=2.0)

        for day_offset in range(DAYS):
            date = START_DATE + timedelta(days=day_offset)
            position = base_position + np.random.normal(0, 2) + np.random.exponential(0.5)
            position = max(0.5, min(100, position))
            ctr = base_ctr * (1 + 0.3 * np.sin(day_offset / 30)) + np.random.normal(0, 0.003)
            ctr = max(0.0001, min(0.5, ctr))
            seasonal = 1 + 0.2 * np.sin(2 * np.pi * day_offset / 365)
            impressions = int(max(0, base_impressions * seasonal * np.random.lognormal(0, 0.1)))
            clicks = int(np.random.poisson(impressions * ctr / 100))

            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "page": page,
                "site": site,
                "impressions": impressions,
                "clicks": clicks,
                "ctr": round(ctr * 100, 4),
                "position": round(position, 2),
            })

        if (i + 1) % 500 == 0:
            print(f"  Generated {i + 1}/{PAGES} pages...")

    df = pd.DataFrame(records)
    df["ctr"] = df["ctr"].clip(0.0001, 50)
    df["position"] = df["position"].clip(0.5, 100)

    out_path = out_dir / "search_performance.csv"
    df.to_csv(str(out_path), index=False)
    print(f"Saved {len(df)} rows to {out_path}")

    meta_df = pd.DataFrame({
        "page": [f"/page-{i:05d}" for i in range(PAGES)],
        "site": np.random.choice(SITES, PAGES),
        "word_count": np.random.lognormal(mean=4.5, sigma=1.0, size=PAGES).astype(int).clip(100, 10000),
        "content_freshness_days": np.random.exponential(scale=180, size=PAGES).astype(int),
        "title_length": np.random.normal(loc=52, scale=12, size=PAGES).astype(int).clip(10, 120),
        "meta_desc_length": np.random.normal(loc=130, scale=40, size=PAGES).astype(int).clip(30, 320),
        "internal_link_count": np.random.poisson(lam=5, size=PAGES),
        "image_count": np.random.poisson(lam=3, size=PAGES),
        "serp_feature_present": np.random.binomial(1, 0.15, size=PAGES),
        "cannibalization_flag": np.random.poisson(lam=0.3, size=PAGES),
        "competitor_avg_position": np.random.normal(loc=8, scale=5, size=PAGES).clip(1, 100),
        "heading_structure_score": np.random.beta(2, 5, size=PAGES),
    })
    meta_df.to_csv(str(out_dir / "page_metadata.csv"), index=False)
    print(f"Saved {len(meta_df)} page metadata rows")


if __name__ == "__main__":
    main()
