# Copyright (c) 2024, Khushi and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

def create_warehouse(warehouse):
	if not frappe.db.exists("Warehouse", warehouse):
		doc = frappe.new_doc("Warehouse")
		doc.is_group = True
		doc.warehouse_name = warehouse
		doc.location = warehouse
		doc.contact = '1234567890'
		doc.save()

def create_item(item,warehouse):
	if not frappe.db.exists("Item", item):
		doc = frappe.new_doc("Item")
		doc.item_code = item
		doc.name1 = item
		doc.opening_warehouse = warehouse
		doc.opening_rate = '22222'
		doc.opening_qty = '12'
		doc.save()
		
class TestItem(FrappeTestCase):
	def setUp(self):
		create_warehouse('Test Warehouse')
		create_item('Test','Test Warehouse')

	def tearDown(self):
		pass
	
	def test_create_item(self):
		doc = frappe.get_last_doc("Item")
		self.assertEqual(doc.name1, 'Test')

	def test_create_Warehouse(self):
		doc = frappe.get_last_doc("Warehouse")
		self.assertEqual(doc.name, 'Test Warehouse')

	def test_create_stock_entry(self):
		doc = frappe.get_last_doc("Stock Entry")
		item = doc.items[0]
		self.assertEqual(item.item_name, 'Test')
