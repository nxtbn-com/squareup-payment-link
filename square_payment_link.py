
import requests
from decimal import Decimal
from typing import Any, Dict
from rest_framework import serializers,status
from nxtbn.order.models import Order
from nxtbn.payment.base import PaymentPlugin, PaymentResponse
from nxtbn.payment import PaymentMethod, PaymentStatus
from square.utilities.webhooks_helper import is_valid_webhook_event_signature
from nxtbn.settings import get_env_var

SQUARE_API_URL = get_env_var('SQUARE_API_URL', 'http://localhost:3000/cart') 
SQUARE_VERSION = '2024-05-15'
SQUARE_ACCESS_TOKEN = get_env_var('SQUARE_ACCESS_TOKEN', 'http://localhost:3000/cart')  
SQUARE_LOCATION_ID = get_env_var('SQUARE_LOCATION_ID', 'http://localhost:3000/cart')
SQUARE_WEBHOOK_SIGNATURE_KEY=get_env_var('SQUARE_WEBHOOK_SIGNATURE_KEY')

class SquareSerializer(serializers.Serializer):
    """Serializer for handling client-side payloads for the Square payment gateway."""
    pass

class SquarePaymentLinkGateway(PaymentPlugin):
    """Square payment gateway implementation."""
    gateway_name = "square_payment_link"
    def authorize(self, amount: Decimal, order_id: str, **kwargs):
        """Authorize a payment with Square."""
        pass  # Implement authorization logic for Square

    def capture(self, amount: Decimal, order_id: str, **kwargs):
        """Capture a previously authorized payment with Square."""
        pass  # Implement capture logic for Square

    def cancel(self, order_id: str, **kwargs):
        """Cancel an authorized payment with Square."""
        pass  # Implement cancellation logic for Square

    def refund(self, amount: Decimal, order_id: str, **kwargs):
        """Refund a captured payment with Square."""
        pass  # Implement refund logic for Square

    def normalize_response(self, raw_response: Any) -> PaymentResponse:
        """Normalize the Square response to a consistent PaymentResponse."""
        pass  # Implement normalization logic for Square response

    def special_serializer(self):
        """Return a serializer for handling client-side payloads in API views."""
        return SquareSerializer()

    def public_keys(self) -> Dict[str, Any]:
        """Retrieve public keys and non-sensitive information for secure communication with Square."""
        return {}

    def payment_url_with_meta(self, order_alias: str, **kwargs) -> Dict[str, Any]:
        """Get payment URL and additional metadata based on the order ID for Square."""
        order = Order.objects.filter(alias=order_alias).first()
        order_items = order.line_items.all()

        total_amount = sum(item.price_per_unit * item.quantity for item in order_items)
        total_amount_cents = int(total_amount * 100)

        payload = {
            "idempotency_key": str(order_alias),
            "quick_pay": {
                "price_money": {
                    "amount": total_amount_cents,
                    "currency": "USD"
                },
                "name": "Order #{}".format(order.alias),
                "location_id": SQUARE_LOCATION_ID
            },
            "payment_note": str(order_alias)
            
        }

   
        headers = {
            'Square-Version': SQUARE_VERSION,
            'Authorization': f'Bearer {SQUARE_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(SQUARE_API_URL, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code != 200:
                return {"error": response_data}

            return {
                "url": response_data['payment_link']['url'],
                "order_alias": order_alias
            }
        except requests.RequestException as e:
            return {"error": str(e)}


    def pretty_request(self, request):
        headers = ''
        for header, value in request.META.items():
            if not header.startswith('HTTP'):
                continue
            header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
            headers += '{}: {}\n'.format(header, value)

        return (
            '{method} HTTP/1.1\n'
            'Content-Length: {content_length}\n'
            'Content-Type: {content_type}\n'
            '{headers}\n\n'
            '{body}'
        ).format(
            method=request.method,
            content_length=request.META['CONTENT_LENGTH'],
            content_type=request.META['CONTENT_TYPE'],
            headers=headers,
            body=request.body,
        )



    def handle_webhook_event(self, request_data: Dict[str, Any], payment_plugin_id: str):
        """
        Handle a webhook event received from Square.
        """
        # Extract payload and signature
        request = request_data
        body = request.body.decode('utf-8')
        square_signature = request.headers.get('X-Square-Hmacsha256-Signature')

        is_from_square = is_valid_webhook_event_signature(body,
                                                          square_signature,
                                                          SQUARE_WEBHOOK_SIGNATURE_KEY,
                                                          request.build_absolute_uri())

        if is_from_square:
            # Signature is valid.
            data = request.data
            print("data",data)
            event_type = data.get("type")

            if event_type == "payment.updated":
                order_alias = data["data"]["object"]["payment"]["note"]

                order = Order.objects.get(alias=order_alias)

                payment_payload = {
                    "order_alias": order_alias,
                    "payment_amount": data["data"]["object"]["payment"]["amount_money"]["amount"],
                    "gateway_response_raw": data,
                    "paid_at": data["data"]["object"]["payment"]["created_at"],
                    "transaction_id": data["data"]["id"],
                    "payment_method": PaymentMethod.CREDIT_CARD,
                    "payment_status": PaymentStatus.CAPTURED,
                    "order": order.pk,
                    "payment_plugin_id": payment_plugin_id,
                    "gateway_name": self.gateway_name,
                }

                self.create_payment_instance(payment_payload)

            return Response(status=status.HTTP_200_OK)
        else:
            # Signature is invalid. Return 403 Forbidden.
            return Response(status=status.HTTP_403_FORBIDDEN)

   
    