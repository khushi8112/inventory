# Copyright (c) 2024, Khushi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint,flt

class StockEntry(Document):

	def validate(self):
		for item in self.items:
			self.validate_item(item)

	def validate_item(self, item):
		if self.type == "Receive" and not item.target_warehouse:
			frappe.throw("Target warehouse is required.")
		elif self.type == "Transfer" and ( not item.target_warehouse or not item.source_warehouse):
			frappe.throw("Target warehouse and Source Warehouse both are required.")
		elif self.type == "Consume" and not item.source_warehouse:
			frappe.throw("Source Warehouse is required")

	def on_submit(self):
		for entry in self.items:
			if self.type == "Receive":
				self.create_stock_ledger(entry, entry.target_warehouse, self.type)
			elif self.type == "Transfer":
				self.create_stock_ledger(entry, entry.target_warehouse, "Receive")
				self.create_stock_ledger(entry, entry.source_warehouse, "Consume")
			else:
				self.create_stock_ledger(entry, entry.source_warehouse, self.type)

	def on_cancel(self):
		for entry in self.items:
			if self.type == "Receive":
				self.create_cancel_entry(entry, entry.target_warehouse, self.type)
			elif self.type == "Transfer":
				self.create_cancel_entry(entry, entry.target_warehouse, "Receive")
				self.create_cancel_entry(entry, entry.source_warehouse, "Consume")
			else:
				self.create_cancel_entry(entry, entry.source_warehouse, self.type)

	def create_stock_ledger(self, entry, warehouse, type):
		item = entry.item_name
		total = self.get_totals(item, warehouse)
		total_qty = total['total_qty']
		total_value = total['total_value']
		quantity = cint(entry.quantity)
		if type == "Receive":
			valuation = (total_value + (int(entry.quantity) * int(entry.item_rate))) / (total_qty + int(entry.quantity))
		elif type == "Consume":
			if cint(entry.quantity) > total_qty:
				frappe.throw("Stock unavailable!")
			quantity = -1 * quantity
			if total_qty + quantity == 0:
				valuation = 0
			else:
				valuation = (total_value + quantity * cint(entry.item_rate)) / (total_qty + quantity)

		qty_change = quantity
		valuation = flt(valuation, precision=2)
		self.insert_sle_entry(entry, warehouse, qty_change, valuation)

	def create_cancel_entry(self, entry, warehouse, type):
		item = entry.item_name
		total = self.get_totals(item, warehouse)
		total_qty = total['total_qty']
		total_value = total['total_value']
		quantity = cint(entry.quantity)
		if type == "Receive":
			if cint(entry.quantity) > total_qty:
				frappe.throw(f"Items at index {entry.idx} got consumed! ")
			quantity = -1 * quantity
			if total_qty + quantity == 0:
				valuation = 0
			else:
				valuation = (total_value + (quantity * cint(entry.item_rate))) / (total_qty + quantity)
		else:
			valuation = (total_value + (quantity * cint(entry.item_rate))) / (total_qty + quantity)

		qty_change = quantity
		valuation = flt(valuation, precision=2)
		self.insert_sle_entry(entry, warehouse, qty_change, valuation)

	def get_totals(self, item, warehouse):
		total_quantity = 0
		total_value = 0
		totals = frappe.db.get_all("Stock Ledger Entry", {
			"item_name": item,
			"warehouse_name": warehouse
		}, ["quantity_change", "inout_rate"])

		for total in totals:
			total_quantity += cint(total.quantity_change)
			total_value += cint(total.quantity_change) * cint(total.inout_rate)

		return {
			"total_qty": total_quantity,
			"total_value": total_value
		}
	

	def insert_sle_entry(self, entry, warehouse, qty_change, valuation):
		doc = frappe.get_doc({
			'doctype': 'Stock Ledger Entry',
			'item_name': entry.item_name,
			'warehouse_name': warehouse,
			'posting_date': self.date,
			'posting_time': self.time,
			'quantity_change': qty_change,
			'inout_rate': entry.item_rate,
			'valuation_rate': valuation,
			'voucher_type': "Stock Entry",
			'voucher_name': self.name
		})
		doc.insert()
	
