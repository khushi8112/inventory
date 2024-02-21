# Copyright (c) 2024, Khushi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StockEntry(Document):

	def before_save(self):
		for item in self.items:
			self.validate_item(item)

	# Validating if required feild have the data based on Stock Entry Type
	def validate_item(self,item):
		if self.type == "Receive":
			if item.target_warehouse is None:
				frappe.throw("Target warehouse is required.")
		elif self.type == "Transfer":
			if item.target_warehouse is None or item.source_warehouse is None :
				frappe.throw("Target warehouse and Source Warehouse both are required.")
		else:
			if item.source_warehouse is None:
				frappe.throw("Source Warehouse is required")



	def on_submit(self):
		if self.type == "Receive":
			self.stock_receive_sle()
		elif self.type == "Transfer":
			self.stock_transfer_sle()
		else:
			self.stock_consume_sle()



	def stock_receive_sle(self):
		for entry in self.items:
			item = entry.item_name
			warehouse = entry.target_warehouse
			# Fetching Total Quantity and Total value
			total = self.get_totals(item,warehouse)
			total_qty = total[0]['total_qty']
			valuation = (total[0]['total_value'] + (int(entry.quantity) * int(entry.item_rate))) / (total_qty + int(entry.quantity))
			posting_date = self.date
			posting_time = self.time
			inout_rate = entry.item_rate
			qty_change = entry.quantity
			self.insert_sle_entry(item,warehouse,posting_date,posting_time,qty_change,inout_rate,valuation)



	def stock_consume_sle(self):
		for entry in self.items:
			item = entry.item_name
			warehouse = entry.source_warehouse
			total = self.get_totals(item,warehouse)
			total_qty = total[0]['total_qty']

			if int(entry.quantity) > total_qty:
				frappe.throw("Stock unavailable!")

			valuation = (total[0]['total_value'] - (int(entry.quantity) * int(entry.item_rate))) / (total_qty - int(entry.quantity))
			posting_date = self.date
			posting_time = self.time
			inout_rate = entry.item_rate
			qty_change = -1 * int(entry.quantity)
			self.insert_sle_entry(item,warehouse,posting_date,posting_time,qty_change,inout_rate,valuation)



	def stock_transfer_sle(self):
		for entry in self.items:
			# Stock Ledger Entry for source warehouse
			item = entry.item_name
			warehouse = entry.source_warehouse
			total = self.get_totals(item,warehouse)
			total_qty = total[0]['total_qty']

			if total_qty < int(entry.quantity):  # Chacking if Stock is available at Source Warehouse to tranfer
				frappe.throw("Stock Unavailable!")

			valuation = (total[0]['total_value'] - (int(entry.quantity) * int(entry.item_rate))) / (total_qty - int(entry.quantity))
			posting_date = self.date
			posting_time = self.time
			inout_rate = entry.item_rate
			qty_change = -1 * int(entry.quantity)
			self.insert_sle_entry(item,warehouse,posting_date,posting_time,qty_change,inout_rate,valuation)	

			# Stock Ledger Entry for Traget Warehouse
			item = entry.item_name
			warehouse = entry.target_warehouse
			total = self.get_totals(item,warehouse)
			total_qty = total[0]['total_qty']
			valuation = (total[0]['total_value'] + (int(entry.quantity) * int(entry.item_rate))) / (total_qty + int(entry.quantity))
			posting_date = self.date
			posting_time = self.time
			inout_rate = entry.item_rate
			qty_change = int(entry.quantity)
			self.insert_sle_entry(item,warehouse,posting_date,posting_time,qty_change,inout_rate,valuation)



	def get_totals(self,item,warehouse):
		total = frappe.db.get_all('Stock Ledger Entry',
					filters = {   # Filtering by item name and warehouse Name
						"item_name":item,
						"warehouse_name":warehouse
					},
    				fields = ['SUM(quantity_change) as total_qty','SUM(quantity_change * inout_rate) as total_value']
		)
		if total[0]['total_qty'] is None :
			total[0]['total_qty'] = 0
		if total[0]['total_value'] is None :
			total[0]['total_value'] = 0

		return total
	

	# Method to Create stock ledger entry 
	def insert_sle_entry(self,item,warehouse,posting_date,posting_time,qty_change,inout_rate,valuation):
		doc = frappe.get_doc({
			'doctype' : 'Stock Ledger Entry',
			'item_name' : item,
			'warehouse_name' : warehouse,
			'posting_date' : posting_date,
			'posting_time' : posting_time,
			'quantity_change' : qty_change,
			'inout_rate' : inout_rate,
			'valuation_rate' : valuation
		})
		# print(doc.as_dict())
		doc.insert()
		# print(doc.docstatus)
		
		
