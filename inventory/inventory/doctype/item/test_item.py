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
		# frappe.delete_doc("Stock Ledger Entry", "Test")
		# frappe.delete_doc("Warehouse", "Test Warehouse")
		# frappe.delete_doc("Item", "Test")
		pass
	
	def test_stock_entry_receive(self):
		doc = self.create_stock_entry("Test", "Test Warehouse", "Receive",2,20)
		self.assertEqual(doc.items[0].item_name, "Test")
		doc = frappe.get_last_doc("Stock Ledger Entry")
		self.assertEqual(doc.item_name, "Test")

	def test_stock_entry_consume(self):
		doc = self.create_stock_entry("Test", "Test Warehouse", "Consume",2,20)
		self.assertEqual(doc.items[0].item_name, "Test")
		doc = frappe.get_last_doc("Stock Ledger Entry")
		self.assertEqual(doc.item_name, "Test")
		self.assertEqual(doc.warehouse_name, "Test Warehouse")

	def test_stock_entry_transfer(self):
		doc = self.create_stock_entry("Test", "Test Warehouse", "Transfer",2,20)
		self.assertEqual(doc.items[0].source_warehouse, "Test Warehouse")
		
	def test_valuation(self):
		self.create_stock_entry("Test","Mumbai","Receive",8,10)
		self.create_stock_entry("Test","Mumbai","Receive",4,20)
		doc = frappe.get_last_doc("Stock Ledger Entry")
		print(doc.valuation_rate)
		self.assertEqual(round(float(doc.valuation_rate),2),13.33)
 
	def create_stock_entry(self,item,warehouse,type,qty,rate):
		se_doc = frappe.new_doc("Stock Entry")
		se_doc.date = today()
		se_doc.time = datetime.now().strftime('%H:%M:%S')
		se_doc.type = type
		if se_doc.type == "Receive":
			se_doc.append('items',
				{
					'item_name' : item,
					'quantity' : qty,
					'item_rate' : rate,
					'target_warehouse' : warehouse,
				}
			)
		elif se_doc.type == "Transfer":
			se_doc.append('items',
				{
					'item_name' : item,
					'quantity' : qty,
					'item_rate' : rate,
					'source_warehouse' : warehouse,
					'target_warehouse' : "Test Warehouse",
				}
			)
		else:
			se_doc.append('items',
				{
					'item_name' : item,
					'quantity' : qty,
					'item_rate' : rate,
					'source_warehouse' : warehouse,
				}
			)
		se_doc.insert()
		se_doc.submit()
		return se_doc
	
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

