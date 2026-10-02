import argparse
import csv
import json
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.glossier.com"
TIMEOUT = 30
SLEEP_SECONDS = 0.2

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; EuromonitorDataEngineeringTest/1.0)",
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
}


def clean_html(value: str) -> str:
    if not value:
        return ""
    return " ".join(BeautifulSoup(value, "html.parser").stripped_strings)


def locale_prefix(locale: str) -> str:
    if locale == "us":
        return ""

    if locale == "in":
        return "/en-in"

    raise ValueError(f"Unsupported locale: {locale}")


def collection_json_url(locale: str) -> str:
    if locale == "us":
        return "https://www.glossier.com/collections/all/products.json"

    if locale == "in":
        return "https://www.glossier.com/en-in/collections/all/products.json"

    raise ValueError(f"Unsupported locale: {locale}")


def product_json_url(locale: str, handle: str) -> str:
    return f"{BASE_URL}{locale_prefix(locale)}/products/{handle}.js"


def product_page_url(locale: str, handle: str) -> str:
    return f"{BASE_URL}{locale_prefix(locale)}/products/{handle}"


def request_json(session: requests.Session, url: str, params=None) -> dict:
    response = session.get(url, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_collection(session: requests.Session, locale: str) -> list[dict]:
    products = []
    page = 1

    while True:
        data = request_json(
            session,
            collection_json_url(locale),
            params={"limit": 250, "page": page},
        )
        batch = data.get("products", [])
        if not batch:
            break

        products.extend(batch)

        if len(batch) < 250:
            break
        page += 1

    return products


def variant_row(
    product: dict,
    variant: dict,
    detail: dict,
    locale: str,
    scraped_at: str,
) -> dict:
    images = detail.get("images") or product.get("images") or []
    variant_id = variant.get("id")

    return {
        "product_name": product.get("title") or detail.get("title") or "",
        "product_id": str(variant_id or product.get("id") or product.get("handle")),
        "image": json.dumps(images, ensure_ascii=False),
        "url": product_page_url(locale, product["handle"]),
        "price": str(variant.get("price", "")),
        "scraped_at": scraped_at,
        "description": clean_html(detail.get("description", "")),
    }


def scrape(locale: str, variants: bool = False) -> list[dict]:
    session = requests.Session()
    session.headers.update(HEADERS)

    scraped_at = datetime.now(timezone.utc).isoformat()
    products = fetch_collection(session, locale)

    if not products:
        raise RuntimeError(
            f"No products returned from {collection_json_url(locale)}. "
            "The locale path or public catalog endpoint may have changed."
        )

    rows = []

    for product in products:
        handle = product.get("handle")
        if not handle:
            continue

        detail = request_json(
            session,
            product_json_url(locale, handle),
        )
        time.sleep(SLEEP_SECONDS)

        product_variants = detail.get("variants") or product.get("variants") or [{}]

        if variants:
            for variant in product_variants:
                rows.append(
                    variant_row(
                        product, variant, detail, locale, scraped_at
                    )
                )
        else:
            rows.append(
                variant_row(
                    product,
                    product_variants[0],
                    detail,
                    locale,
                    scraped_at,
                )
            )

    return rows


def write_csv(rows: list[dict], output_path: str) -> None:
    fields = [
        "product_name",
        "product_id",
        "image",
        "url",
        "price",
        "scraped_at",
        "description",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Glossier Shop All.")
    parser.add_argument(
        "--locale",
        choices=["in", "us"],
        default="in",
        help="Glossier market/locale: in or us.",
    )
    parser.add_argument(
        "--variants",
        action="store_true",
        help="Treat each Shopify variant as a unique product.",
    )
    parser.add_argument(
        "--output",
        default="glossier_products.csv",
        help="Output CSV path.",
    )
    args = parser.parse_args()

    rows = scrape(args.locale, args.variants)
    write_csv(rows, args.output)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
