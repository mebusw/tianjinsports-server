from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.test import TestCase

class PaginatorTest(TestCase):
    def testPages(self):
        objects = ['john', 'paul', 'george', 'ringo']
        p = Paginator(objects, 2)

        self.assertEqual(4, p.count)
        self.assertEqual(2, p.num_pages)
        self.assertEqual([1, 2], p.page_range)
        self.assertEqual(['john', 'paul'], p.page(1).object_list)
        self.assertFalse(p.page(2).has_next())
        self.assertEqual(3, p.page(2).start_index())
