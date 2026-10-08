"""
Roll B: Data Processing (Andmete töötlemine)
Andmed päritakse data_fetcher.py-st ja töödeldakse siin
"""
import pandas as pd
from data_fetcher import fetch_sales, fetch_customers, fetch_products


def clean_data(df):
    """
    Andmete puhastamine
    """

    df_clean = df.copy()

    print("Alustan andmete puhastamist...")
    print("Algne shape:", df_clean.shape)

    # Duplikaatide kontroll ja eemaldamine
    duplicate_count = df_clean.duplicated(
        subset=["invoice_id"]
    ).sum()

    print("Duplikaate invoice_id järgi:", duplicate_count)

    df_clean = df_clean.drop_duplicates(
        subset=["invoice_id"],
        keep="first"
    )

    print("Shape pärast duplikaatide eemaldamist:", df_clean.shape)

    # NULL väärtuste kontroll
    null_count = df_clean[
        ["customer_id", "sale_date", "total_price"]
    ].isna().any(axis=1).sum()

    print("NULL väärtustega ridu:", null_count)

    # NULL väärtuste eemaldamine
    df_clean = df_clean.dropna(
        subset=["customer_id", "sale_date", "total_price"]
    )

    print("Shape pärast NULL-ide eemaldamist:", df_clean.shape)

    # Kuupäevade teisendamine datetime formaati
    df_clean["sale_date"] = pd.to_datetime(
        df_clean["sale_date"],
        errors="coerce"
    )

    # Vigaste kuupäevade kontroll
    invalid_dates = df_clean["sale_date"].isna().sum()

    print("Vigase kuupäevaga ridu:", invalid_dates)

    # Vigaste kuupäevade eemaldamine
    df_clean = df_clean.dropna(
        subset=["sale_date"]
    )

    # Null- ja negatiivsete müügisummade kontroll
    # total_price teisendamine numbriliseks
    df_clean["total_price"] = pd.to_numeric(
        df_clean["total_price"],
        errors="coerce"
    )

    # Teisendamisel tekkinud vigaste väärtuste eemaldamine
    df_clean = df_clean.dropna(
        subset=["total_price"]
    )

    # Null- ja negatiivsete müügisummade kontroll
    negative_prices = (
        df_clean["total_price"] <= 0
    ).sum()

    print(
        "Null või negatiivse total_price väärtusega ridu:",
        negative_prices
    )

    # Null- ja negatiivsete müügisummade eemaldamine
    df_clean = df_clean[
        df_clean["total_price"] > 0
    ].copy()

    print(
        "Shape pärast vigaste müügisummade eemaldamist:",
        df_clean.shape
    )

    print("Andmete puhastamine lõpetatud.")

    return df_clean


def calculate_weekly_aggregates(df):
    """
    Arvutab nädalate kaupa:
    - käibe
    - tellimuste arvu
    - keskmise tellimuste väärtuse
    """

    print("Arvutan nädalased koondnäitajad...")

    required_columns = ["sale_date", "total_price"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Puuduv vajalik veerg: {column}")

    df_temp = df.copy()

    # Kontroll, et sale_date oleks datetime
    if not pd.api.types.is_datetime64_any_dtype(df_temp["sale_date"]):
        df_temp["sale_date"] = pd.to_datetime(
            df_temp["sale_date"],
            errors="coerce"
        )

    weekly = (
        df_temp
        .resample("W", on="sale_date")
        .agg(
            revenue=("total_price", "sum"),
            orders=("total_price", "count"),
            avg_order_value=("total_price", "mean")
        )
        .reset_index()
    )

    print(f"Nädalaid kokku: {len(weekly)}")

    return weekly


def calculate_kpis(df):
    """
    Arvutan KPI-d
    """

    print("Arvutan KPI-d...")

    required_columns = [
        "total_price",
        "customer_id"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Puuduv vajalik veerg: {column}")

    total_revenue = df["total_price"].sum()
    unique_customers = df["customer_id"].nunique()

    # Kui olemas on invoice_id, kasutame tellimuste arvu selle järgi
    if "invoice_id" in df.columns:
        order_count = df["invoice_id"].nunique()
    else:
        order_count = len(df)

    if order_count > 0:
        avg_order_value = total_revenue / order_count
    else:
        avg_order_value = 0

    kpis = {
        "total_revenue": total_revenue,
        "unique_customers": unique_customers,
        "avg_order_value": avg_order_value
    }

    print("KPI-d arvutatud.")

    return kpis


def merge_datasets(df_sales, df_customers):
    """
    Liidab müügi- ja kliendiandmed customer_id alusel
    """

    print("Liidan müügi- ja kliendiandmed...")

    if "customer_id" not in df_sales.columns:
        raise ValueError(
            "Müügiandmetes puudub customer_id veerg."
        )

    if "customer_id" not in df_customers.columns:
        raise ValueError(
            "Kliendiandmetes puudub customer_id veerg."
        )

    merged_df = pd.merge(
        df_sales,
        df_customers,
        on="customer_id",
        how="left",
        validate="m:1"
    )

    print(f"Liidetud andmestikus ridu: {len(merged_df)}")

    return merged_df


if __name__ == "__main__":
    # Testimise osa ajalise filtriga
    sales_data = fetch_sales("2023-01-01", "2025-02-28")
    customers_data = fetch_customers()
    products_data = fetch_products()

    print("\n--- PÄRITUD ANDMED ---")
    print("Müük:", sales_data.shape)
    print("Kliendid:", customers_data.shape)
    print("Tooted:", products_data.shape)

    # Müügiandmete puhastamine
    sales_clean = clean_data(sales_data)

    # Nädalased koondnäitajad
    weekly_result = calculate_weekly_aggregates(sales_clean)

    print("\n--- NÄDALASED KOONDNÄITAJAD ---")
    print(weekly_result.head())

    # KPI-d
    kpi_result = calculate_kpis(sales_clean)

    print("\n--- KPI-D ---")
    print(kpi_result)

    # Müügi- ja kliendiandmete ühendamine
    merged_result = merge_datasets(
        sales_clean,
        customers_data
    )

    print("\n--- LIIDETUD ANDMED ---")
    print(merged_result.head())
