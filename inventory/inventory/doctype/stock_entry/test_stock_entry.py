# Copyright (c) 2024, Khushi and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today,datetime,flt
from inventory.inventory.doctype.item.test_item import create_item, create_warehouse
from datetime import datetime


def create_stock_entry(item, warehouse, type, qty, rate):
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


class TestStockEntry(FrappeTestCase):
    def setUp(self):
        create_warehouse('Test Warehouse')
        create_item('Test','Test Warehouse')

    def tearDown(self):
        pass

    def test_stock_entry_receive(self):
        doc = create_stock_entry("Test", "Test Warehouse", "Receive", 2, 20).submit()
        # Checking if Stock Entry is created
        latest_doc = frappe.db.exists("Stock Entry", doc.name)
        self.assertTrue(latest_doc)

        # Checking if Stock Ledger Entry is created
        latest_doc = frappe.get_last_doc("Stock Ledger Entry")
        self.assertEqual(latest_doc.warehouse_name, "Test Warehouse")
        self.assertEqual(latest_doc.voucher_name, doc.name)

    def test_stock_entry_consume(self):
        doc = create_stock_entry("Test", "Test Warehouse", "Consume", 2, 20).submit()
        # Checking if Stock Entry is created
        latest_doc = frappe.db.exists("Stock Entry", doc.name)
        self.assertTrue(latest_doc)

        # Checking if Stock Ledger Entry is created
        latest_doc = frappe.get_last_doc("Stock Ledger Entry")
        self.assertEqual(latest_doc.item_name, "Test")
        self.assertEqual(latest_doc.warehouse_name, "Test Warehouse")
        self.assertEqual(latest_doc.voucher_name, doc.name)

    def test_stock_entry_transfer(self):
        create_warehouse("My Warehouse")
        create_item("Camera", "My Warehouse")
        doc = create_stock_entry("Camera", "My Warehouse", "Transfer", 2, 20).submit()
        # Checking if Stock Entry is created
        latest_doc = frappe.db.exists("Stock Entry", doc.name)
        self.assertTrue(latest_doc)

        # Checking if Stock Ledger Entry is created
        latest_doc = frappe.get_last_doc("Stock Ledger Entry")
        self.assertEqual(latest_doc.item_name, "Camera")
        self.assertEqual(latest_doc.warehouse_name, "My Warehouse")
        self.assertEqual(latest_doc.voucher_name, doc.name)

    def test_stock_availability(self):
        doc = create_stock_entry("Test", "Test Warehouse", "Consume", 200, 20)
        self.assertRaises(frappe.ValidationError,doc.submit)

    def test_valuation(self):
        create_warehouse("My Warehouse")
        create_item("My Item", "My Warehouse")
        doc = create_stock_entry("My Item", "My Warehouse", "Receive", 8, 1500).submit()
        doc = create_stock_entry("My Item", "My Warehouse", "Receive", 4, 1800).submit()
        doc = frappe.get_last_doc("Stock Ledger Entry")
        self.assertEqual(flt((doc.valuation_rate),2),1800)

    def test_on_cancel_valuation(self):
        create_warehouse("My Warehouse")
        doc = create_stock_entry("Test", "My Warehouse", "Receive", 8, 10).submit()
        doc = create_stock_entry("Test", "My Warehouse", "Receive", 4, 20).submit()
        doc = create_stock_entry("Test", "My Warehouse", "Receive", 10, 30).submit()
        doc.cancel()
        latest_doc = frappe.get_last_doc("Stock Ledger Entry")
        self.assertEqual(flt(latest_doc.valuation_rate), 13.33)

