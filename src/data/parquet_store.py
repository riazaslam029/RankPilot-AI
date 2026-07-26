from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from src.utils.logging import get_logger

logger = get_logger(__name__)


def write_parquet(df, filepath: str, partition_cols: list[str] | None = None) -> None:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    table = pa.Table.from_pandas(df)

    if partition_cols:
        pq.write_to_dataset(
            table,
            str(path.parent),
            partition_cols=partition_cols,
            compression="snappy",
        )
    else:
        pq.write_table(table, str(path), compression="snappy")

    logger.info(f"Wrote {len(df)} rows to {path}")


def read_parquet(filepath: str) -> "pd.DataFrame":
    import pandas as pd

    path = Path(filepath)
    if not path.exists():
        logger.warning(f"Parquet file does not exist: {path}")
        return pd.DataFrame()

    df = pd.read_parquet(str(path))
    logger.info(f"Read {len(df)} rows from {path}")
    return df
