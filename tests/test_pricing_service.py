import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError


class TestPricingService(unittest.TestCase):

	def setUp(self):
		self.ps = PricingService()

	# ── subtotal_cents ──

	def test_subtotal_single_item(self):
		items = [CartItem("A", 1000, 2)]
		self.assertEqual(self.ps.subtotal_cents(items), 2000)

	def test_subtotal_multiple_items(self):
		items = [CartItem("A", 500, 3), CartItem("B", 200, 1)]
		self.assertEqual(self.ps.subtotal_cents(items), 1700)

	def test_subtotal_empty_cart(self):
		self.assertEqual(self.ps.subtotal_cents([]), 0)

	def test_subtotal_qty_zero_raises(self):
		with self.assertRaises(PricingError):
			self.ps.subtotal_cents([CartItem("A", 100, 0)])

	def test_subtotal_qty_negative_raises(self):
		with self.assertRaises(PricingError):
			self.ps.subtotal_cents([CartItem("A", 100, -1)])

	def test_subtotal_negative_price_raises(self):
		with self.assertRaises(PricingError):
			self.ps.subtotal_cents([CartItem("A", -10, 1)])

	# ── apply_coupon ──

	def test_coupon_none(self):
		self.assertEqual(self.ps.apply_coupon(10000, None), 10000)

	def test_coupon_empty_string(self):
		self.assertEqual(self.ps.apply_coupon(10000, ""), 10000)

	def test_coupon_spaces_only(self):
		self.assertEqual(self.ps.apply_coupon(10000, "   "), 10000)

	def test_coupon_save10(self):
		self.assertEqual(self.ps.apply_coupon(10000, "SAVE10"), 9000)

	def test_coupon_save10_lowercase(self):
		self.assertEqual(self.ps.apply_coupon(10000, " save10 "), 9000)

	def test_coupon_clp2000(self):
		self.assertEqual(self.ps.apply_coupon(10000, "CLP2000"), 8000)

	def test_coupon_clp2000_below_zero(self):
		self.assertEqual(self.ps.apply_coupon(1000, "CLP2000"), 0)

	def test_coupon_invalid_raises(self):
		with self.assertRaises(PricingError):
			self.ps.apply_coupon(10000, "BADCODE")

	# ── tax_cents ──

	def test_tax_cl(self):
		self.assertEqual(self.ps.tax_cents(10000, "CL"), 1900)

	def test_tax_eu(self):
		self.assertEqual(self.ps.tax_cents(10000, "EU"), 2100)

	def test_tax_us(self):
		self.assertEqual(self.ps.tax_cents(10000, "US"), 0)

	def test_tax_unsupported_country(self):
		with self.assertRaises(PricingError):
			self.ps.tax_cents(10000, "JP")

	def test_tax_country_with_spaces(self):
		self.assertEqual(self.ps.tax_cents(10000, " cl "), 1900)

	# ── shipping_cents ──

	def test_shipping_cl_free(self):
		self.assertEqual(self.ps.shipping_cents(20000, "CL"), 0)

	def test_shipping_cl_paid(self):
		self.assertEqual(self.ps.shipping_cents(19999, "CL"), 2500)

	def test_shipping_us(self):
		self.assertEqual(self.ps.shipping_cents(10000, "US"), 5000)

	def test_shipping_eu(self):
		self.assertEqual(self.ps.shipping_cents(10000, "EU"), 5000)

	def test_shipping_unsupported_country(self):
		with self.assertRaises(PricingError):
			self.ps.shipping_cents(10000, "JP")

	# ── total_cents ──

	def test_total_cents_cl_no_coupon(self):
		items = [CartItem("A", 10000, 3)]  # subtotal 30000
		# net=30000, tax=5700, shipping=0 -> 35700
		self.assertEqual(self.ps.total_cents(items, None, "CL"), 35700)

	def test_total_cents_with_coupon(self):
		items = [CartItem("A", 5000, 2)]  # subtotal 10000
		# SAVE10 -> net=9000, tax CL=1710, shipping=2500 -> 13210
		self.assertEqual(self.ps.total_cents(items, "SAVE10", "CL"), 13210)
