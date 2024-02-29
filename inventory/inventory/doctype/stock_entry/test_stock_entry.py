# Copyright (c) 2024, Khushi and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today,datetime,flt
from datetime import datetime

class TestStockEntry(FrappeTestCase):
    def setUp(self):
        self.create_warehouse('Test Warehouse')
        self.create_item('Test','Test Warehouse')

    def tearDown(self):
        pass

    def test_stock_entry_receive(self):
        doc = self.create_stock_entry("Test", "Test Warehouse", "Receive", 2, 20).submit()
        # Checking if Stock Entry is created
        latest_doc = frappe.db.exists("Stock Entry", doc.name)
        self.assertTrue(latest_doc)

        # Checking if Stock Ledger Entry is created
        latest_doc = frappe.get_last_doc("Stock Ledger Entry")
        self.assertEqual(latest_doc.warehouse_name, "Test Warehouse")
        self.assertEqual(int(latest_doc.quantity_change), 2)

    def test_stock_entry_consume(self):
        doc = self.create_stock_entry("Test", "Test Warehouse", "Consume", 2, 20).submit()
        # Checking if Stock Entry is created
        latest_doc = frappe.db.exists("Stock Entry", doc.name)
        self.assertTrue(latest_doc)

        # Checking if Stock Ledger Entry is created
        latest_doc = frappe.get_last_doc("Stock Ledger Entry")
        self.assertEqual(latest_doc.item_name, "Test")
        self.assertEqual(latest_doc.warehouse_name, "Test Warehouse")
        self.assertEqual(int(latest_doc.quantity_change), -2)

    def test_stock_entry_transfer(self):
        doc = self.create_stock_entry("Laptop", "Mumbai", "Transfer", 2, 20).submit()
        # Checking if Stock Entry is created
        latest_doc = frappe.db.exists("Stock Entry", doc.name)
        self.assertTrue(latest_doc)

        # Checking if Stock Ledger Entry is created
        latest_doc = frappe.get_last_doc("Stock Ledger Entry")
        self.assertEqual(latest_doc.item_name, "Laptop")
        self.assertEqual(latest_doc.warehouse_name, "Mumbai")
        self.assertEqual(int(latest_doc.quantity_change), -2)

    def test_stock_availability(self):
        doc = self.create_stock_entry("Test", "Test Warehouse", "Consume", 200, 20)
        self.assertRaises(frappe.ValidationError,doc.submit)

    def test_valuation(self):
        doc = self.create_stock_entry("Main Item", "Main", "Receive", 8, 10).submit()
        doc = self.create_stock_entry("Main Item", "Main", "Receive", 4, 20).submit()
        doc = frappe.get_last_doc("Stock Ledger Entry")

        self.assertEqual(round(float(doc.valuation_rate),2),13.33)

    def test_on_cancel_valuation(self):
        doc = self.create_stock_entry("Test", "Mumbai", "Receive", 8, 10).submit()
        doc = self.create_stock_entry("Test", "Mumbai", "Receive", 4, 20).submit()
        doc = self.create_stock_entry("Test", "Mumbai", "Receive", 10, 30).submit()
        doc.cancel()
        latest_doc = frappe.get_last_doc("Stock Ledger Entry")
        # self.assertEqual(round(float(latest_doc.valuation_rate),2),13.33)
        self.assertEqual(flt(latest_doc.valuation_rate), 13.33)

    def create_stock_entry(self, item, warehouse, type, qty, rate):
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
        se_doc.save()
        return se_doc
    
    def create_warehouse(self, warehouse):
        if not frappe.db.exists("Warehouse", warehouse):
            doc = frappe.new_doc("Warehouse")
            doc.is_group = True
            doc.warehouse_name = warehouse
            doc.location = warehouse
            doc.contact = '1234567890'
            doc.save()

    def create_item(self, item, warehouse):
        if not frappe.db.exists("Item", item):
            doc = frappe.new_doc("Item")
            doc.item_code = item
            doc.name1 = item
            doc.opening_warehouse = warehouse
            doc.opening_rate = '22222'
            doc.opening_qty = '12'
            doc.save()