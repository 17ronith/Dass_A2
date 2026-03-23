import os
from typing import Any, Dict, List, Optional

import pytest
import requests


BASE_URL = os.getenv("QUICKCART_BASE_URL", "http://localhost:8080/api/v1")
ROLL_NUMBER = os.getenv("QUICKCART_ROLL", "123")
USER_ID = os.getenv("QUICKCART_USER_ID", "799")


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL.rstrip("/")


@pytest.fixture(scope="session")
def roll_header() -> Dict[str, str]:
    return {"X-Roll-Number": str(ROLL_NUMBER)}


@pytest.fixture(scope="session")
def user_headers(roll_header: Dict[str, str]) -> Dict[str, str]:
    headers = dict(roll_header)
    headers["X-User-ID"] = str(USER_ID)
    return headers


def _get_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except ValueError:
        return None


def _extract_list(data: Any, key: str) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and key in data and isinstance(data[key], list):
        return data[key]
    return []


def _admin_get(base_url: str, roll_header: Dict[str, str], path: str) -> requests.Response:
    return requests.get(f"{base_url}{path}", headers=roll_header, timeout=10)


def _user_get(base_url: str, user_headers: Dict[str, str], path: str) -> requests.Response:
    return requests.get(f"{base_url}{path}", headers=user_headers, timeout=10)


def _user_post(base_url: str, user_headers: Dict[str, str], path: str, payload: Dict[str, Any]) -> requests.Response:
    return requests.post(
        f"{base_url}{path}",
        headers=user_headers,
        json=payload,
        timeout=10,
    )


def _user_put(base_url: str, user_headers: Dict[str, str], path: str, payload: Dict[str, Any]) -> requests.Response:
    return requests.put(
        f"{base_url}{path}",
        headers=user_headers,
        json=payload,
        timeout=10,
    )


def _user_delete(base_url: str, user_headers: Dict[str, str], path: str) -> requests.Response:
    return requests.delete(f"{base_url}{path}", headers=user_headers, timeout=10)


def _find_first(items: List[Dict[str, Any]], key: str, value: Any) -> Optional[Dict[str, Any]]:
    for item in items:
        if item.get(key) == value:
            return item
    return None


def _get_admin_users(base_url: str, roll_header: Dict[str, str]) -> List[Dict[str, Any]]:
    resp = _admin_get(base_url, roll_header, "/admin/users")
    assert resp.status_code == 200
    data = _get_json(resp)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "users" in data:
        return data["users"]
    return []


def _get_admin_products(base_url: str, roll_header: Dict[str, str]) -> List[Dict[str, Any]]:
    resp = _admin_get(base_url, roll_header, "/admin/products")
    assert resp.status_code == 200
    data = _get_json(resp)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "products" in data:
        return data["products"]
    return []


def _get_admin_coupons(base_url: str, roll_header: Dict[str, str]) -> List[Dict[str, Any]]:
    resp = _admin_get(base_url, roll_header, "/admin/coupons")
    assert resp.status_code == 200
    data = _get_json(resp)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "coupons" in data:
        return data["coupons"]
    return []


def _get_admin_orders(base_url: str, roll_header: Dict[str, str]) -> List[Dict[str, Any]]:
    resp = _admin_get(base_url, roll_header, "/admin/orders")
    assert resp.status_code == 200
    data = _get_json(resp)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "orders" in data:
        return data["orders"]
    return []


def _pick_product_for_cart(products: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for product in products:
        if product.get("active", True) and product.get("stock", 0) > 0:
            return product
    return None


def _pick_product_with_min_stock(
    products: List[Dict[str, Any]],
    min_stock: int,
) -> Optional[Dict[str, Any]]:
    for product in products:
        if product.get("active", True) and product.get("stock", 0) >= min_stock:
            return product
    return None


def test_missing_roll_header_admin(base_url: str) -> None:
    resp = requests.get(f"{base_url}/admin/users", timeout=10)
    assert resp.status_code == 401


def test_invalid_roll_header_admin(base_url: str) -> None:
    resp = requests.get(
        f"{base_url}/admin/users",
        headers={"X-Roll-Number": "abc"},
        timeout=10,
    )
    assert resp.status_code == 400


def test_missing_user_header_user_endpoint(base_url: str, roll_header: Dict[str, str]) -> None:
    resp = requests.get(f"{base_url}/profile", headers=roll_header, timeout=10)
    assert resp.status_code == 400


def test_missing_roll_header_user_endpoint(base_url: str) -> None:
    resp = requests.get(f"{base_url}/profile", headers={"X-User-ID": str(USER_ID)}, timeout=10)
    assert resp.status_code == 401


def test_invalid_roll_header_user_endpoint(base_url: str) -> None:
    resp = requests.get(
        f"{base_url}/profile",
        headers={"X-Roll-Number": "abc", "X-User-ID": str(USER_ID)},
        timeout=10,
    )
    assert resp.status_code == 400


def test_invalid_user_header_non_integer(base_url: str, roll_header: Dict[str, str]) -> None:
    headers = dict(roll_header)
    headers["X-User-ID"] = "abc"
    resp = requests.get(f"{base_url}/profile", headers=headers, timeout=10)
    assert resp.status_code == 400


def test_invalid_user_header_negative(base_url: str, roll_header: Dict[str, str]) -> None:
    headers = dict(roll_header)
    headers["X-User-ID"] = "-1"
    resp = requests.get(f"{base_url}/profile", headers=headers, timeout=10)
    assert resp.status_code == 400


def test_profile_get(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_get(base_url, user_headers, "/profile")
    assert resp.status_code == 200
    data = _get_json(resp)
    assert data is not None


def test_profile_update_invalid_name(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"name": "A", "phone": "9922663637"}
    resp = _user_put(base_url, user_headers, "/profile", payload)
    assert resp.status_code == 400


def test_profile_update_invalid_phone(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"name": "Valid Name", "phone": "123"}
    resp = _user_put(base_url, user_headers, "/profile", payload)
    assert resp.status_code == 400


def test_profile_update_name_too_long(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"name": "A" * 51, "phone": "9922663637"}
    resp = _user_put(base_url, user_headers, "/profile", payload)
    assert resp.status_code == 400


def test_profile_update_phone_non_digit(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"name": "Valid Name", "phone": "12345abcde"}
    resp = _user_put(base_url, user_headers, "/profile", payload)
    assert resp.status_code == 400


def test_profile_update_valid_no_change(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_get(base_url, user_headers, "/profile")
    assert resp.status_code == 200
    profile = _get_json(resp) or {}
    name = profile.get("name")
    phone = profile.get("phone")
    if not name or not phone:
        pytest.skip("Profile missing name or phone")
    update_resp = _user_put(base_url, user_headers, "/profile", {"name": name, "phone": phone})
    assert update_resp.status_code == 200


def test_addresses_add_invalid_label(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {
        "label": "INVALID",
        "street": "123 Main Street",
        "city": "Metropolis",
        "pincode": "123456",
        "is_default": False,
    }
    resp = _user_post(base_url, user_headers, "/addresses", payload)
    assert resp.status_code == 400


def test_addresses_add_label_lowercase(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {
        "label": "home",
        "street": "123 Main Street",
        "city": "Metropolis",
        "pincode": "123456",
        "is_default": False,
    }
    resp = _user_post(base_url, user_headers, "/addresses", payload)
    assert resp.status_code == 400


def test_addresses_add_invalid_street_length(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {
        "label": "HOME",
        "street": "123",
        "city": "Metropolis",
        "pincode": "123456",
        "is_default": False,
    }
    resp = _user_post(base_url, user_headers, "/addresses", payload)
    assert resp.status_code == 400


def test_addresses_add_invalid_city_length(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {
        "label": "HOME",
        "street": "123 Main Street",
        "city": "M",
        "pincode": "123456",
        "is_default": False,
    }
    resp = _user_post(base_url, user_headers, "/addresses", payload)
    assert resp.status_code == 400


def test_addresses_add_invalid_pincode_length(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {
        "label": "HOME",
        "street": "123 Main Street",
        "city": "Metropolis",
        "pincode": "12345",
        "is_default": False,
    }
    resp = _user_post(base_url, user_headers, "/addresses", payload)
    assert resp.status_code == 400


def test_addresses_add_invalid_pincode_non_digit(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {
        "label": "HOME",
        "street": "123 Main Street",
        "city": "Metropolis",
        "pincode": "12a456",
        "is_default": False,
    }
    resp = _user_post(base_url, user_headers, "/addresses", payload)
    assert resp.status_code == 400


def test_addresses_add_update_delete_flow(base_url: str, user_headers: Dict[str, str]) -> None:
    created_ids: List[int] = []

    payload1 = {
        "label": "HOME",
        "street": "123 Main Street",
        "city": "Metropolis",
        "pincode": "123456",
        "is_default": True,
    }
    resp1 = _user_post(base_url, user_headers, "/addresses", payload1)
    assert resp1.status_code == 200
    data1 = _get_json(resp1)
    assert data1 is not None
    address1 = data1.get("address", data1)
    addr_id1 = address1.get("address_id")
    assert addr_id1 is not None
    created_ids.append(addr_id1)

    payload2 = {
        "label": "OFFICE",
        "street": "456 Side Street",
        "city": "Metropolis",
        "pincode": "654321",
        "is_default": True,
    }
    resp2 = _user_post(base_url, user_headers, "/addresses", payload2)
    assert resp2.status_code == 200
    data2 = _get_json(resp2)
    assert data2 is not None
    address2 = data2.get("address", data2)
    addr_id2 = address2.get("address_id")
    assert addr_id2 is not None
    created_ids.append(addr_id2)

    list_resp = _user_get(base_url, user_headers, "/addresses")
    assert list_resp.status_code == 200
    addresses = _get_json(list_resp) or []
    if isinstance(addresses, dict) and "addresses" in addresses:
        addresses = addresses["addresses"]
    default_count = sum(1 for addr in addresses if addr.get("is_default"))
    assert default_count == 1

    update_payload = {"street": "789 New Street", "is_default": False}
    update_resp = _user_put(base_url, user_headers, f"/addresses/{addr_id1}", update_payload)
    assert update_resp.status_code == 200
    updated = _get_json(update_resp)
    updated_addr = updated.get("address", updated)
    assert updated_addr.get("street") == "789 New Street"

    for addr_id in created_ids:
        _user_delete(base_url, user_headers, f"/addresses/{addr_id}")


def test_addresses_delete_missing(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_delete(base_url, user_headers, "/addresses/99999999")
    assert resp.status_code == 404


def test_addresses_get_list(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_get(base_url, user_headers, "/addresses")
    assert resp.status_code == 200


def test_products_list_excludes_inactive(
    base_url: str,
    roll_header: Dict[str, str],
    user_headers: Dict[str, str],
) -> None:
    admin_products = _get_admin_products(base_url, roll_header)
    inactive = _find_first(admin_products, "active", False)
    if not inactive:
        pytest.skip("No inactive products found")
    resp = requests.get(f"{base_url}/products", headers=user_headers, timeout=10)
    assert resp.status_code == 200
    data = _get_json(resp) or []
    if isinstance(data, dict) and "products" in data:
        data = data["products"]
    ids = {prod.get("product_id") for prod in data}
    assert inactive.get("product_id") not in ids


def test_products_get_not_found(
    base_url: str,
    roll_header: Dict[str, str],
    user_headers: Dict[str, str],
) -> None:
    admin_products = _get_admin_products(base_url, roll_header)
    max_id = max((p.get("product_id", 0) for p in admin_products), default=0)
    resp = requests.get(
        f"{base_url}/products/{max_id + 9999}",
        headers=user_headers,
        timeout=10,
    )
    assert resp.status_code == 404


def test_products_get_active_product(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    admin_products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(admin_products)
    if not product:
        pytest.skip("No active product with stock found")
    product_id = product.get("product_id")
    resp = _user_get(base_url, user_headers, f"/products/{product_id}")
    assert resp.status_code == 200
    data = _get_json(resp) or {}
    assert data.get("product_id") == product_id


def test_products_filter_by_category(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    admin_products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(admin_products)
    if not product:
        pytest.skip("No product to derive category")
    category = product.get("category")
    if not category:
        pytest.skip("Product category missing")
    resp = requests.get(
        f"{base_url}/products",
        headers=user_headers,
        params={"category": category},
        timeout=10,
    )
    assert resp.status_code == 200
    data = _extract_list(_get_json(resp) or [], "products")
    if not data:
        pytest.skip("No products returned for category")
    assert all(prod.get("category") == category for prod in data)


def test_products_search_by_name(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    admin_products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(admin_products)
    if not product:
        pytest.skip("No product to derive name")
    name = product.get("name")
    if not name or len(name) < 3:
        pytest.skip("Product name missing or too short")
    query = name[:3]
    resp = requests.get(
        f"{base_url}/products",
        headers=user_headers,
        params={"search": query},
        timeout=10,
    )
    assert resp.status_code == 200
    data = _extract_list(_get_json(resp) or [], "products")
    if not data:
        pytest.skip("No products returned for search")
    assert all(query.lower() in (prod.get("name", "").lower()) for prod in data)


def test_products_prices_match_admin_sample(
    base_url: str,
    roll_header: Dict[str, str],
    user_headers: Dict[str, str],
) -> None:
    admin_products = _get_admin_products(base_url, roll_header)
    sample = [p for p in admin_products if p.get("active", True)][:3]
    if not sample:
        pytest.skip("No active products to sample")
    for product in sample:
        product_id = product.get("product_id")
        resp = _user_get(base_url, user_headers, f"/products/{product_id}")
        assert resp.status_code == 200
        data = _get_json(resp) or {}
        assert data.get("price") == product.get("price")


def test_cart_add_invalid_quantity(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"product_id": 1, "quantity": 0}
    resp = _user_post(base_url, user_headers, "/cart/add", payload)
    assert resp.status_code == 400


def test_cart_add_nonexistent_product(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    admin_products = _get_admin_products(base_url, roll_header)
    max_id = max((p.get("product_id", 0) for p in admin_products), default=0)
    resp = _user_post(base_url, user_headers, "/cart/add", {"product_id": max_id + 9999, "quantity": 1})
    assert resp.status_code == 404


def test_cart_add_negative_quantity(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"product_id": 1, "quantity": -1}
    resp = _user_post(base_url, user_headers, "/cart/add", payload)
    assert resp.status_code == 400


def test_cart_add_and_totals(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    _user_delete(base_url, user_headers, "/cart/clear")

    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(products)
    if not product:
        pytest.skip("No active product with stock found")

    product_id = product.get("product_id")
    price = product.get("price")
    quantity = 2

    resp = _user_post(base_url, user_headers, "/cart/add", {"product_id": product_id, "quantity": quantity})
    assert resp.status_code == 200

    cart_resp = _user_get(base_url, user_headers, "/cart")
    assert cart_resp.status_code == 200
    cart = _get_json(cart_resp) or {}
    items = cart.get("items", cart.get("cart_items", cart))
    if isinstance(items, dict):
        items = items.get("items", [])

    item = _find_first(items, "product_id", product_id)
    assert item is not None
    assert item.get("quantity") == quantity
    assert item.get("subtotal") == pytest.approx(quantity * price, rel=1e-3)

    total = cart.get("total", cart.get("cart_total"))
    if total is not None:
        subtotals = [it.get("subtotal", 0) for it in items]
        assert total == pytest.approx(sum(subtotals), rel=1e-3)

    _user_delete(base_url, user_headers, "/cart/clear")


def test_cart_add_exceeds_stock(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    _user_delete(base_url, user_headers, "/cart/clear")

    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(products)
    if not product:
        pytest.skip("No active product with stock found")

    product_id = product.get("product_id")
    stock = int(product.get("stock", 0))
    resp = _user_post(base_url, user_headers, "/cart/add", {"product_id": product_id, "quantity": stock + 1})
    assert resp.status_code == 400


def test_cart_add_same_product_accumulates(
    base_url: str,
    roll_header: Dict[str, str],
    user_headers: Dict[str, str],
) -> None:
    _user_delete(base_url, user_headers, "/cart/clear")

    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_with_min_stock(products, 2)
    if not product:
        pytest.skip("No product with stock >= 2 found")

    product_id = product.get("product_id")
    resp = _user_post(base_url, user_headers, "/cart/add", {"product_id": product_id, "quantity": 1})
    assert resp.status_code == 200
    resp = _user_post(base_url, user_headers, "/cart/add", {"product_id": product_id, "quantity": 1})
    assert resp.status_code == 200

    cart_resp = _user_get(base_url, user_headers, "/cart")
    assert cart_resp.status_code == 200
    cart = _get_json(cart_resp) or {}
    items = cart.get("items", cart.get("cart_items", cart))
    if isinstance(items, dict):
        items = items.get("items", [])

    item = _find_first(items, "product_id", product_id)
    assert item is not None
    assert item.get("quantity") == 2

    _user_delete(base_url, user_headers, "/cart/clear")


def test_cart_update_invalid_quantity(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"product_id": 1, "quantity": 0}
    resp = _user_post(base_url, user_headers, "/cart/update", payload)
    assert resp.status_code == 400


def test_cart_update_valid_quantity(
    base_url: str,
    roll_header: Dict[str, str],
    user_headers: Dict[str, str],
) -> None:
    _user_delete(base_url, user_headers, "/cart/clear")

    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_with_min_stock(products, 3)
    if not product:
        pytest.skip("No product with stock >= 3 found")

    product_id = product.get("product_id")
    resp = _user_post(base_url, user_headers, "/cart/add", {"product_id": product_id, "quantity": 1})
    assert resp.status_code == 200
    resp = _user_post(base_url, user_headers, "/cart/update", {"product_id": product_id, "quantity": 3})
    assert resp.status_code == 200

    cart_resp = _user_get(base_url, user_headers, "/cart")
    assert cart_resp.status_code == 200
    cart = _get_json(cart_resp) or {}
    items = cart.get("items", cart.get("cart_items", cart))
    if isinstance(items, dict):
        items = items.get("items", [])

    item = _find_first(items, "product_id", product_id)
    assert item is not None
    assert item.get("quantity") == 3

    _user_delete(base_url, user_headers, "/cart/clear")


def test_cart_update_negative_quantity(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"product_id": 1, "quantity": -2}
    resp = _user_post(base_url, user_headers, "/cart/update", payload)
    assert resp.status_code == 400


def test_cart_remove_missing(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"product_id": 999999}
    resp = _user_post(base_url, user_headers, "/cart/remove", payload)
    assert resp.status_code == 404


def test_cart_remove_existing(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    _user_delete(base_url, user_headers, "/cart/clear")

    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(products)
    if not product:
        pytest.skip("No product available for cart")

    product_id = product.get("product_id")
    resp = _user_post(base_url, user_headers, "/cart/add", {"product_id": product_id, "quantity": 1})
    assert resp.status_code == 200

    resp = _user_post(base_url, user_headers, "/cart/remove", {"product_id": product_id})
    assert resp.status_code == 200

    cart_resp = _user_get(base_url, user_headers, "/cart")
    assert cart_resp.status_code == 200
    cart = _get_json(cart_resp) or {}
    items = cart.get("items", cart.get("cart_items", cart))
    if isinstance(items, dict):
        items = items.get("items", [])
    assert _find_first(items, "product_id", product_id) is None

    _user_delete(base_url, user_headers, "/cart/clear")


def test_cart_clear_empties(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(products)
    if not product:
        pytest.skip("No product available for cart")

    product_id = product.get("product_id")
    resp = _user_post(base_url, user_headers, "/cart/add", {"product_id": product_id, "quantity": 1})
    assert resp.status_code == 200

    clear_resp = _user_delete(base_url, user_headers, "/cart/clear")
    assert clear_resp.status_code == 200

    cart_resp = _user_get(base_url, user_headers, "/cart")
    assert cart_resp.status_code == 200
    cart = _get_json(cart_resp) or {}
    items = cart.get("items", cart.get("cart_items", cart))
    if isinstance(items, dict):
        items = items.get("items", [])
    assert len(items) == 0


def test_coupon_apply_expired_or_minimum(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    coupons = _get_admin_coupons(base_url, roll_header)
    if not coupons:
        pytest.skip("No coupons found")

    coupon = coupons[0]
    code = coupon.get("code") or coupon.get("coupon_code")
    if not code:
        pytest.skip("No coupon code found")

    resp = _user_post(base_url, user_headers, "/coupon/apply", {"code": code})
    assert resp.status_code in {200, 400}


def test_checkout_empty_cart(base_url: str, user_headers: Dict[str, str]) -> None:
    _user_delete(base_url, user_headers, "/cart/clear")
    resp = _user_post(base_url, user_headers, "/checkout", {"payment_method": "COD"})
    assert resp.status_code == 400


def test_checkout_invalid_payment_method(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_post(base_url, user_headers, "/checkout", {"payment_method": "CASH"})
    assert resp.status_code == 400


def test_checkout_cod_over_limit(
    base_url: str,
    roll_header: Dict[str, str],
    user_headers: Dict[str, str],
) -> None:
    _user_delete(base_url, user_headers, "/cart/clear")

    products = _get_admin_products(base_url, roll_header)
    active_products = [p for p in products if p.get("active", True) and p.get("stock", 0) > 0]
    if not active_products:
        pytest.skip("No active products with stock found")

    total = 0.0
    for product in active_products:
        if total > 5000:
            break
        product_id = product.get("product_id")
        price = float(product.get("price", 0))
        if price <= 0:
            continue
        resp = _user_post(base_url, user_headers, "/cart/add", {"product_id": product_id, "quantity": 1})
        if resp.status_code == 200:
            total += price

    if total <= 5000:
        pytest.skip("Could not build cart total above 5000")

    resp = _user_post(base_url, user_headers, "/checkout", {"payment_method": "COD"})
    assert resp.status_code == 400

    _user_delete(base_url, user_headers, "/cart/clear")


def test_wallet_add_invalid_amount(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_post(base_url, user_headers, "/wallet/add", {"amount": 0})
    assert resp.status_code == 400


def test_wallet_get_balance(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_get(base_url, user_headers, "/wallet")
    assert resp.status_code == 200
    data = _get_json(resp) or {}
    assert "balance" in data or "wallet_balance" in data


def test_wallet_add_valid_amount(base_url: str, user_headers: Dict[str, str]) -> None:
    before_resp = _user_get(base_url, user_headers, "/wallet")
    assert before_resp.status_code == 200
    before = _get_json(before_resp) or {}
    balance_before = float(before.get("balance", before.get("wallet_balance", 0)))

    add_resp = _user_post(base_url, user_headers, "/wallet/add", {"amount": 1})
    assert add_resp.status_code == 200

    after_resp = _user_get(base_url, user_headers, "/wallet")
    assert after_resp.status_code == 200
    after = _get_json(after_resp) or {}
    balance_after = float(after.get("balance", after.get("wallet_balance", 0)))
    assert balance_after == pytest.approx(balance_before + 1, rel=1e-3)


def test_wallet_add_too_large_amount(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_post(base_url, user_headers, "/wallet/add", {"amount": 100001})
    assert resp.status_code == 400


def test_wallet_pay_insufficient(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    users = _get_admin_users(base_url, roll_header)
    user = _find_first(users, "user_id", int(USER_ID))
    if not user:
        pytest.skip("User not found in admin list")
    balance = float(user.get("wallet_balance", 0))

    resp = _user_post(base_url, user_headers, "/wallet/pay", {"amount": balance + 1000})
    assert resp.status_code == 400


def test_wallet_pay_invalid_amount(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_post(base_url, user_headers, "/wallet/pay", {"amount": 0})
    assert resp.status_code == 400


def test_wallet_pay_valid_amount(base_url: str, user_headers: Dict[str, str]) -> None:
    add_resp = _user_post(base_url, user_headers, "/wallet/add", {"amount": 1})
    assert add_resp.status_code == 200
    before_resp = _user_get(base_url, user_headers, "/wallet")
    assert before_resp.status_code == 200
    before = _get_json(before_resp) or {}
    balance_before = float(before.get("balance", before.get("wallet_balance", 0)))
    if balance_before < 1:
        pytest.skip("Wallet balance too low for pay test")
    pay_resp = _user_post(base_url, user_headers, "/wallet/pay", {"amount": 1})
    assert pay_resp.status_code == 200
    after_resp = _user_get(base_url, user_headers, "/wallet")
    assert after_resp.status_code == 200
    after = _get_json(after_resp) or {}
    balance_after = float(after.get("balance", after.get("wallet_balance", 0)))
    assert balance_after == pytest.approx(balance_before - 1, rel=1e-3)


def test_loyalty_redeem_invalid_amount(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_post(base_url, user_headers, "/loyalty/redeem", {"amount": 0})
    assert resp.status_code == 400


def test_loyalty_get_points(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_get(base_url, user_headers, "/loyalty")
    assert resp.status_code == 200
    data = _get_json(resp) or {}
    assert "points" in data or "loyalty_points" in data


def test_loyalty_redeem_insufficient_points(
    base_url: str,
    roll_header: Dict[str, str],
    user_headers: Dict[str, str],
) -> None:
    users = _get_admin_users(base_url, roll_header)
    user = _find_first(users, "user_id", int(USER_ID))
    if not user:
        pytest.skip("User not found in admin list")
    points = int(user.get("loyalty_points", 0))
    resp = _user_post(base_url, user_headers, "/loyalty/redeem", {"amount": points + 1})
    assert resp.status_code == 400


def test_loyalty_redeem_valid_if_points(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_get(base_url, user_headers, "/loyalty")
    assert resp.status_code == 200
    data = _get_json(resp) or {}
    points = int(data.get("points", data.get("loyalty_points", 0)))
    if points < 1:
        pytest.skip("Not enough points to redeem")
    redeem_resp = _user_post(base_url, user_headers, "/loyalty/redeem", {"amount": 1})
    assert redeem_resp.status_code == 200


def test_order_cancel_missing(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_post(base_url, user_headers, "/orders/999999/cancel", {})
    assert resp.status_code == 404


def test_orders_get_list(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_get(base_url, user_headers, "/orders")
    assert resp.status_code == 200


def test_orders_get_detail(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_get(base_url, user_headers, "/orders")
    assert resp.status_code == 200
    orders = _extract_list(_get_json(resp) or [], "orders")
    if not orders:
        pytest.skip("No orders available")
    order_id = orders[0].get("order_id")
    detail_resp = _user_get(base_url, user_headers, f"/orders/{order_id}")
    assert detail_resp.status_code == 200


def test_orders_invoice_totals(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_get(base_url, user_headers, "/orders")
    assert resp.status_code == 200
    orders = _extract_list(_get_json(resp) or [], "orders")
    if not orders:
        pytest.skip("No orders available")
    order_id = orders[0].get("order_id")
    invoice_resp = _user_get(base_url, user_headers, f"/orders/{order_id}/invoice")
    assert invoice_resp.status_code == 200
    invoice = _get_json(invoice_resp) or {}
    subtotal = float(invoice.get("subtotal", 0))
    gst = float(invoice.get("gst", invoice.get("gst_amount", 0)))
    total = float(invoice.get("total", 0))
    if subtotal == 0 and total == 0:
        pytest.skip("Invoice missing totals")
    assert total == pytest.approx(subtotal + gst, rel=1e-3)


def test_reviews_invalid_rating(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(products)
    if not product:
        pytest.skip("No product for review")

    product_id = product.get("product_id")
    payload = {"rating": 6, "comment": "Too high rating"}
    resp = _user_post(base_url, user_headers, f"/products/{product_id}/reviews", payload)
    assert resp.status_code == 400


def test_reviews_get_list(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(products)
    if not product:
        pytest.skip("No product for review list")
    product_id = product.get("product_id")
    resp = _user_get(base_url, user_headers, f"/products/{product_id}/reviews")
    assert resp.status_code == 200


def test_reviews_add_valid(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(products)
    if not product:
        pytest.skip("No product for valid review")
    product_id = product.get("product_id")
    payload = {"rating": 5, "comment": "Great product"}
    resp = _user_post(base_url, user_headers, f"/products/{product_id}/reviews", payload)
    assert resp.status_code == 200


def test_reviews_invalid_comment_length(
    base_url: str,
    roll_header: Dict[str, str],
    user_headers: Dict[str, str],
) -> None:
    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(products)
    if not product:
        pytest.skip("No product for review")

    product_id = product.get("product_id")
    payload = {"rating": 5, "comment": "A" * 201}
    resp = _user_post(base_url, user_headers, f"/products/{product_id}/reviews", payload)
    assert resp.status_code == 400


def test_reviews_empty_comment(
    base_url: str,
    roll_header: Dict[str, str],
    user_headers: Dict[str, str],
) -> None:
    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(products)
    if not product:
        pytest.skip("No product for review")

    product_id = product.get("product_id")
    payload = {"rating": 4, "comment": ""}
    resp = _user_post(base_url, user_headers, f"/products/{product_id}/reviews", payload)
    assert resp.status_code == 400


def test_support_ticket_status_flow(base_url: str, user_headers: Dict[str, str]) -> None:
    create_payload = {"subject": "Order issue", "message": "Need help with my order."}
    create_resp = _user_post(base_url, user_headers, "/support/ticket", create_payload)
    assert create_resp.status_code == 200
    ticket_data = _get_json(create_resp)
    ticket = ticket_data.get("ticket", ticket_data)
    ticket_id = ticket.get("ticket_id")
    assert ticket_id is not None

    update_resp = _user_put(base_url, user_headers, f"/support/tickets/{ticket_id}", {"status": "IN_PROGRESS"})
    assert update_resp.status_code == 200

    update_resp = _user_put(base_url, user_headers, f"/support/tickets/{ticket_id}", {"status": "CLOSED"})
    assert update_resp.status_code == 200

    invalid_resp = _user_put(base_url, user_headers, f"/support/tickets/{ticket_id}", {"status": "OPEN"})
    assert invalid_resp.status_code == 400


def test_support_tickets_list_contains_new(base_url: str, user_headers: Dict[str, str]) -> None:
    create_payload = {"subject": "Delivery delay", "message": "Package arrived late."}
    create_resp = _user_post(base_url, user_headers, "/support/ticket", create_payload)
    assert create_resp.status_code == 200
    ticket_data = _get_json(create_resp) or {}
    ticket = ticket_data.get("ticket", ticket_data)
    ticket_id = ticket.get("ticket_id")
    if not ticket_id:
        pytest.skip("Ticket id missing in create response")

    list_resp = _user_get(base_url, user_headers, "/support/tickets")
    assert list_resp.status_code == 200
    tickets = _extract_list(_get_json(list_resp) or [], "tickets")
    assert any(t.get("ticket_id") == ticket_id for t in tickets)


def test_support_ticket_invalid_subject(base_url: str, user_headers: Dict[str, str]) -> None:
    create_payload = {"subject": "Bad", "message": "Valid message"}
    create_resp = _user_post(base_url, user_headers, "/support/ticket", create_payload)
    assert create_resp.status_code == 400


def test_support_ticket_invalid_message_empty(base_url: str, user_headers: Dict[str, str]) -> None:
    create_payload = {"subject": "Valid subject", "message": ""}
    create_resp = _user_post(base_url, user_headers, "/support/ticket", create_payload)
    assert create_resp.status_code == 400


def test_support_ticket_invalid_message_length(base_url: str, user_headers: Dict[str, str]) -> None:
    create_payload = {"subject": "Valid subject", "message": "A" * 501}
    create_resp = _user_post(base_url, user_headers, "/support/ticket", create_payload)
    assert create_resp.status_code == 400


def test_order_cancel_delivered_order(
    base_url: str,
    roll_header: Dict[str, str],
    user_headers: Dict[str, str],
) -> None:
    orders = _get_admin_orders(base_url, roll_header)
    delivered = _find_first(orders, "status", "DELIVERED")
    if not delivered:
        pytest.skip("No delivered order found")

    order_id = delivered.get("order_id")
    resp = _user_post(base_url, user_headers, f"/orders/{order_id}/cancel", {})
    assert resp.status_code == 400
