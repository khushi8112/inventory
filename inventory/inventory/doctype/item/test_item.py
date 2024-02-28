# Copyright (c) 2024, Khushi and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import cint,today
from datetime import datetime


class TestItem(FrappeTestCase):
	def setUp(self):
		self.create_warehouse('Test Warehouse')
		self.create_item('Test','Test Warehouse')

	def tearDown(self):
		pass
	
	def test_create_item(self):
		doc = frappe.get_last_doc("Item")
		self.assertEqual(doc.name1, 'Test')

	def test_create_Warehouse(self):
		doc = frappe.get_last_doc("Warehouse")
		self.assertEqual(doc.name, 'Test Warehouse')

	def create_warehouse(self,warehouse):
		if not frappe.db.exists("Warehouse", warehouse):
			doc = frappe.new_doc("Warehouse")
			doc.is_group = True
			doc.warehouse_name = warehouse
			doc.location = warehouse
			doc.contact = '1234567890'
			doc.save()

	def create_item(self,item,warehouse):
		if not frappe.db.exists("Item", item):
			doc = frappe.new_doc("Item")
			doc.item_code = item
			doc.name1 = item
			doc.opening_warehouse = warehouse
			doc.opening_rate = '22222'
			doc.opening_qty = '12'
			doc.save()
			# frappe.db.commit()

