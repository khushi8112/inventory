# Copyright (c) 2024, Khushi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today,get_time,now_datetime
from datetime import datetime

class Item(Document):
	
	def after_insert(self):
		self.create_stock_entry()
		self.insert_sle_entry()

	def create_stock_entry(self):
		se_doc = frappe.new_doc("Stock Entry")
		se_doc.date = today()
		se_doc.time = datetime.now().strftime('%H:%M:%S')
		se_doc.type = "Receive"
		# se_doc.insert()
		se_doc.save()
		
		item_doc = frappe.new_doc("Stock Entry Items")
		item_doc.item_name = self.name
		item_doc.quantity = self.opening_qty
		item_doc.item_rate = self.opening_rate
		item_doc.target_warehouse = self.opening_warehouse
		item_doc.parent = se_doc.name
		item_doc.parentfield = "items"
		item_doc.parenttype = "Stock Entry"
		item_doc.save()
		se_doc.submit()
		
		""" se_doc = frappe.new_doc("Stock Entry")
		print(type(se_doc.items))
		se_doc.date = today()
		se_doc.time = datetime.now().strftime('%H:%M:%S')
		se_doc.type = "Receive"
		se_doc.items = [
			{
				'item_name' : self.name,
				'quantity' : self.opening_qty,
				'item_rate' : self.opening_rate,
				'target_warehouse' : self.opening_warehouse,
			}
		]
		se_doc.insert() """


	def insert_sle_entry(self):
		sle_doc = frappe.new_doc("Stock Ledger Entry")
		sle_doc.item_name = self.name
		sle_doc.warehouse_name  = self.opening_warehouse
		sle_doc.posting_date = today()
		sle_doc.posting_time = datetime.now().strftime('%H:%M:%S')
		sle_doc.quantity_change = self.opening_qty
		sle_doc.inout_rate = self.opening_rate
		sle_doc.valuation_rate = self.opening_rate
		sle_doc.insert()

