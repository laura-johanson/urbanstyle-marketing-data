"""
Roll D: Automation Script (Automatiseerimisskript)

Ühendab andmete pärimise, töötlemise, visualiseerimise
ja eksportimise üheks pipeline'iks.
"""

import logging
import time

from data_fetcher import fetch_sales, fetch_customers, fetch_products
from transform import (
    clean_data,
    calculate_weekly_aggregates,
    calculate_kpis,
    merge_datasets
)
from visualize_export import (
    create_weekly_chart,
    create_kpi_summary,
    export_results
)


# Logimise seadistus
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_pipeline():
    """
    Käivitab kogu UrbanStyle pipeline'i:
    extract -> transform -> visualize -> export.
    """

    try:
        logging.info("Pipeline käivitus.")

        # -----------------------------------------
        # 1. EXTRACT
        # -----------------------------------------

        logging.info("Extract etapp algas.")

        sales_data = fetch_sales(
            "2023-01-01",
            "2025-02-28"
        )
        customers_data = fetch_customers()
        products_data = fetch_products()

        logging.info(
            "Extract valmis: müük %s rida, kliendid %s rida, tooted %s rida.",
            len(sales_data),
            len(customers_data),
            len(products_data)
        )

        # -----------------------------------------
        # 2. TRANSFORM
        # -----------------------------------------

        logging.info("Transform etapp algas.")

        sales_clean = clean_data(
            sales_data
        )

        weekly_result = calculate_weekly_aggregates(
            sales_clean
        )

        kpi_result = calculate_kpis(
            sales_clean
        )

        merged_result = merge_datasets(
            sales_clean,
            customers_data
        )

        logging.info(
            "Transform valmis: puhastatud müük %s rida, "
            "nädalaid %s, liidetud andmestik %s rida.",
            len(sales_clean),
            len(weekly_result),
            len(merged_result)
        )

        # -----------------------------------------
        # 3. VISUALIZE
        # -----------------------------------------

        logging.info("Visualiseerimise etapp algas.")

        weekly_chart = create_weekly_chart(
            weekly_result
        )

        kpi_chart = create_kpi_summary(
            kpi_result
        )

        logging.info("Visualiseerimise etapp valmis.")

        # -----------------------------------------
        # 4. EXPORT
        # -----------------------------------------

        logging.info("Ekspordi etapp algas.")

        export_results(
            weekly_result,
            "output",
            weekly_chart,
            kpi_chart
        )

        logging.info("Ekspordi etapp valmis.")

        # -----------------------------------------
        # 5. KOKKUVÕTE
        # -----------------------------------------

        logging.info("Pipeline lõpetatud edukalt.")

        print("\n--- PIPELINE KOKKUVÕTE ---")
        print(f"Puhastatud müügiridu: {len(sales_clean)}")
        print(f"Nädalaid kokku: {len(weekly_result)}")
        print(f"Unikaalseid kliente: {kpi_result['unique_customers']}")
        print(f"Kogukäive: {kpi_result['total_revenue']:.2f} €")
        print(
            f"Keskmine tellimuse väärtus: "
            f"{kpi_result['avg_order_value']:.2f} €"
        )

    except Exception as error:  # pylint: disable=broad-exception-caught
        logging.error(
            "Pipeline ebaõnnestus: %s",
            error
        )


if __name__ == "__main__":

    start_time = time.time()

    run_pipeline()

    elapsed_time = time.time() - start_time

    print(
        f"\nPipeline tööaeg: {elapsed_time:.2f} sekundit"
    )
