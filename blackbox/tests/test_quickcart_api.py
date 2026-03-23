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


def _pick_product_for_cart(products: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for product in products:
        if product.get("active", True) and product.get("stock", 0) > 0:
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


def test_cart_add_invalid_quantity(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"product_id": 1, "quantity": 0}
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


def test_cart_update_invalid_quantity(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"product_id": 1, "quantity": 0}
    resp = _user_post(base_url, user_headers, "/cart/update", payload)
    assert resp.status_code == 400


def test_cart_remove_missing(base_url: str, user_headers: Dict[str, str]) -> None:
    payload = {"product_id": 999999}
    resp = _user_post(base_url, user_headers, "/cart/remove", payload)
    assert resp.status_code == 404


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


def test_wallet_add_invalid_amount(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_post(base_url, user_headers, "/wallet/add", {"amount": 0})
    assert resp.status_code == 400


def test_wallet_pay_insufficient(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    users = _get_admin_users(base_url, roll_header)
    user = _find_first(users, "user_id", int(USER_ID))
    if not user:
        pytest.skip("User not found in admin list")
    balance = float(user.get("wallet_balance", 0))

    resp = _user_post(base_url, user_headers, "/wallet/pay", {"amount": balance + 1000})
    assert resp.status_code == 400


def test_loyalty_redeem_invalid_amount(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_post(base_url, user_headers, "/loyalty/redeem", {"amount": 0})
    assert resp.status_code == 400


def test_order_cancel_missing(base_url: str, user_headers: Dict[str, str]) -> None:
    resp = _user_post(base_url, user_headers, "/orders/999999/cancel", {})
    assert resp.status_code == 404


def test_reviews_invalid_rating(base_url: str, roll_header: Dict[str, str], user_headers: Dict[str, str]) -> None:
    products = _get_admin_products(base_url, roll_header)
    product = _pick_product_for_cart(products)
    if not product:
        pytest.skip("No product for review")

    product_id = product.get("product_id")
    payload = {"rating": 6, "comment": "Too high rating"}
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
