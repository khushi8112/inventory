import frappe
from frappe.tests.utils import FrappeTestCase
from inventory.inventory.doctype.item.test_item import create_item, create_warehouse
from inventory.inventory.doctype.stock_entry.test_stock_entry import create_stock_entry
from inventory.inventory.report.stock_ledger.stock_ledger import execute

class TestStockBalanceReport(FrappeTestCase):
    def setUp(self):
        create_warehouse("My Warehouse")
        create_item("My Item", "My Warehouse")

    def tearDown(self):
        pass

    def test_stock_balance_report(self):
        create_stock_entry("My Item", "My Warehouse", "Receive", 30, 50).submit()
        doc = create_stock_entry("My Item", "My Warehouse", "Consume", 12, 40).submit()

        expected_data = frappe._dict({
            'item_name': 'My Item',
            'warehouse_name': 'My Warehouse',
            'inout_rate': '40',
            'quantity_change': '-12',
            'valuation_rate': '8922.8',
            'voucher_name': doc.name
        })
        
        filters = frappe._dict({'item_name': "My Item", 'warehouse_name': "My Warehouse"})

        columns, data = execute(filters)
        for key in expected_data:
            self.assertEqual(data[0].key, expected_data.key)
        