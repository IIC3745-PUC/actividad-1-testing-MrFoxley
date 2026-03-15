import unittest
from unittest.mock import Mock, patch, ANY

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError
from src.checkout import CheckoutService, ChargeResult


class TestCheckoutService(unittest.TestCase):

	def setUp(self):
		self.payments = Mock()
		self.email = Mock()
		self.fraud = Mock()
		self.repo = Mock()
		self.pricing = Mock(spec=PricingService)

		self.service = CheckoutService(
			payments=self.payments,
			email=self.email,
			fraud=self.fraud,
			repo=self.repo,
			pricing=self.pricing,
		)
		self.items = [CartItem("SKU1", 1000, 2)]

	# ── invalid user ──

	def test_empty_user_returns_invalid(self):
		result = self.service.checkout("", self.items, "tok", "CL")
		self.assertEqual(result, "INVALID_USER")

	def test_spaces_only_user_returns_invalid(self):
		result = self.service.checkout("   ", self.items, "tok", "CL")
		self.assertEqual(result, "INVALID_USER")

	# ── pricing error ──

	def test_pricing_error_returns_invalid_cart(self):
		self.pricing.total_cents.side_effect = PricingError("qty must be > 0")
		result = self.service.checkout("user1", self.items, "tok", "CL")
		self.assertIn("INVALID_CART", result)

	# ── fraud rejection ──

	def test_fraud_score_high_returns_rejected(self):
		self.pricing.total_cents.return_value = 5000
		self.fraud.score.return_value = 80
		result = self.service.checkout("user1", self.items, "tok", "CL")
		self.assertEqual(result, "REJECTED_FRAUD")

	def test_fraud_score_below_threshold_passes(self):
		self.pricing.total_cents.return_value = 5000
		self.fraud.score.return_value = 79
		self.payments.charge.return_value = ChargeResult(ok=True, charge_id="ch_1")
		result = self.service.checkout("user1", self.items, "tok", "CL")
		self.assertTrue(result.startswith("OK:"))

	# ── payment failed ──

	def test_payment_failed_returns_reason(self):
		self.pricing.total_cents.return_value = 5000
		self.fraud.score.return_value = 10
		self.payments.charge.return_value = ChargeResult(ok=False, reason="declined")
		result = self.service.checkout("user1", self.items, "tok", "CL")
		self.assertEqual(result, "PAYMENT_FAILED:declined")

	# ── successful checkout ──

	def test_successful_checkout_saves_order_and_sends_receipt(self):
		self.pricing.total_cents.return_value = 5000
		self.fraud.score.return_value = 10
		self.payments.charge.return_value = ChargeResult(ok=True, charge_id="ch_123")

		result = self.service.checkout("user1", self.items, "tok_abc", "CL", coupon_code="SAVE10")

		self.assertTrue(result.startswith("OK:"))
		order_id = result.split(":")[1]

		self.repo.save.assert_called_once()
		saved_order = self.repo.save.call_args[0][0]
		self.assertEqual(saved_order.user_id, "user1")
		self.assertEqual(saved_order.total_cents, 5000)
		self.assertEqual(saved_order.payment_charge_id, "ch_123")
		self.assertEqual(saved_order.coupon_code, "SAVE10")
		self.assertEqual(saved_order.country, "CL")

		self.email.send_receipt.assert_called_once_with("user1", order_id, 5000)

	def test_successful_checkout_charge_id_none_uses_unknown(self):
		self.pricing.total_cents.return_value = 3000
		self.fraud.score.return_value = 0
		self.payments.charge.return_value = ChargeResult(ok=True, charge_id=None)

		result = self.service.checkout("user1", self.items, "tok", "CL")

		self.assertTrue(result.startswith("OK:"))
		saved_order = self.repo.save.call_args[0][0]
		self.assertEqual(saved_order.payment_charge_id, "UNKNOWN")

	# ── default pricing ──

	def test_default_pricing_service_is_created(self):
		service = CheckoutService(
			payments=self.payments,
			email=self.email,
			fraud=self.fraud,
			repo=self.repo,
		)
		self.assertIsInstance(service.pricing, PricingService)
