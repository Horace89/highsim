import unittest

from simil import order_symbol_1, symbols, id_and_symbols, cmp_to_key, \
                    PrefixIndexing, PrefixPositionIndexing, PrefixPositionLengthIndexing

#run with: python -m unittest -v mytests.py


class TestOrdersWithStrings(unittest.TestCase):

    def test_order_symbol1(self):
        self.assertEqual(order_symbol_1('a'), 1)

    def test_symbols_remove_duplicates(self):
        self.assertTupleEqual(symbols("dabd", order=order_symbol_1),  ('a', 'b', 'd'))

    def test_symbols_respect_order(self):
        s = "dab"
        s_symbols = symbols(s, order=order_symbol_1)
        self.assertTupleEqual(s_symbols, ('a', 'b', 'd'))

        order_values = list(map(order_symbol_1, s_symbols))
        #print('order_values:', order_values)
        self.assertTrue(all(earlier <= later for earlier, later in zip(order_values, order_values[1:])))


class TestPrefixPositionLengthIndexing(unittest.TestCase):

    def test_prefix_length(self):
        J = 0.9
        pi = PrefixIndexing(None, J)
        self.assertEqual(pi.prefix_length("*" * 9), 1)
        self.assertEqual(pi.prefix_length("*" * 10), 2)
        self.assertEqual(pi.prefix_length("*" * 19), 2)
        self.assertEqual(pi.prefix_length("*" * 20), 3)

    def test_make_many_to_one_index_1(self):
        list_of_strings = ["acdefghijk", "abdefghijk"]
        J = 0.8
        pi = PrefixPositionLengthIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertSetEqual(set(pi.ii.keys()), set([('a', 1, 9), ('b', 2, 8), ('c', 2, 8), ('d', 3, 7)]))
        self.assertDictEqual(pi.ii, {('a', 1, 9): {0, 1}, ('b', 2, 8): {1}, ('c', 2, 8): {0}, ('d', 3, 7): {0, 1}})

    #@unittest.skip("not yet!")
    def test_make_many_to_one_index_2(self):
        list_of_strings = ["bcdefghij", "abcdefghij", "cdefghijklm", "aefghijkluvw"]
        J = 0.8
        pi = PrefixPositionLengthIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertDictEqual(pi.ii, { ('a', 1, 9): {1},
                                      ('a', 1, 11): {3},
                                      ('b', 1, 8): {0},
                                      ('b', 2, 8): {1},
                                      ('c', 1, 10): {2},
                                      ('c', 2, 7): {0},
                                      ('c', 3, 7): {1},
                                      ('d', 2, 9): {2},
                                      ('e', 2, 10): {3},
                                      ('e', 3, 8): {2},
                                      ('f', 3, 9): {3} })

    #@unittest.skip("not yet!")
    def test_candidate_pairs_1(self):
        list_of_strings = ["bcdefghij", "abcdefghij"]
        J = 0.8
        pi = PrefixPositionLengthIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertSetEqual(set(pi.candidate_pairs("aefghijklmno")), {1})
        #self.assertSetEqual(pi.cp_keys, {('a', 1)})

    #@unittest.skip("not yet!")
    def test_candidate_pairs_2(self):
        list_of_strings = ["bcdefghij", "abcdefghij", "cdefghijklm", "aefghijkluvw"]
        J = 0.8
        pi = PrefixPositionLengthIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertSetEqual(set(pi.candidate_pairs("aefghijklmno")), {1, 3})
        #self.assertSetEqual(pi.cp_keys, {('a', 1)})


class TestPrefixIndexing(unittest.TestCase):

    # def setUp(self):
    #     list_of_strings = ["bcdefghij", "abcdefghij", "cdefghijklm", "aefghijkluvw"]
    #     J = 0.9
    #     self.pi = PrefixIndexing(list_of_strings, J)
    #     pi.make_prefix_index()
    #     print("ii:", pi.ii)
    #     pi.display()
    #     cp = pi.candidate_pairs("aefghijklmno")
    #     print("cp:", cp)

    def test_prefix_length(self):
        J = 0.9
        pi = PrefixIndexing(None, J)
        self.assertEqual(pi.prefix_length("*" * 9), 1)
        self.assertEqual(pi.prefix_length("*" * 10), 2)
        self.assertEqual(pi.prefix_length("*" * 19), 2)
        self.assertEqual(pi.prefix_length("*" * 20), 3)

    def test_make_many_to_one_index_1(self):
        list_of_strings = ["bcdefghij", "abcdefghij"]
        J = 0.9
        pi = PrefixIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertSetEqual(set(pi.ii.keys()), set(['a', 'b']))
        self.assertDictEqual(pi.ii, {'b': {0, 1}, 'a': {1}})

    def test_make_many_to_one_index_2(self):
        list_of_strings = ["bcdefghij", "abcdefghij", "cdefghijklm", "aefghijkluvw"]
        J = 0.9
        pi = PrefixIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertSetEqual(set(pi.ii.keys()), set(['a', 'b', 'c', 'd', 'e']))
        self.assertDictEqual(pi.ii, {'a': {1, 3}, 'c': {2}, 'e': {3}, 'd': {2}, 'b': {0, 1}})

    def test_candidate_pairs_1(self):
        list_of_strings = ["bcdefghij", "abcdefghij"]
        J = 0.9
        pi = PrefixIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertSetEqual(pi.candidate_pairs("aefghijklmno"), {1})
        self.assertSetEqual(pi.cp_keys, {'a'})

    def test_candidate_pairs_2(self):
        list_of_strings = ["bcdefghij", "abcdefghij", "cdefghijklm", "aefghijkluvw"]
        J = 0.9
        pi = PrefixIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertSetEqual(pi.candidate_pairs("aefghijklmno"), {1, 3})
        self.assertSetEqual(pi.cp_keys, {'a', 'e'})

#@unittest.skip
class TestPrefixPositionIndexing(unittest.TestCase):

    def test_make_many_to_one_index_1(self):
        list_of_strings = ["bcdefghij", "abcdefghij"]
        J = 0.9
        pi = PrefixPositionIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertSetEqual(set(pi.ii.keys()), set([('a', 1), ('b', 1), ('b', 2)]))
        self.assertDictEqual(pi.ii, {('a', 1): {1}, ('b', 1): {0}, ('b', 2): {1}})

    def test_make_many_to_one_index_2(self):
        list_of_strings = ["bcdefghij", "abcdefghij", "cdefghijklm", "aefghijkluvw"]
        J = 0.9
        pi = PrefixPositionIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertDictEqual(pi.ii, { ('a', 1): {1, 3},
                                      ('b', 1): {0},
                                      ('b', 2): {1},
                                      ('c', 1): {2},
                                      ('d', 2): {2},
                                      ('e', 2): {3} })

    def test_candidate_pairs_1(self):
        list_of_strings = ["bcdefghij", "abcdefghij"]
        J = 0.9
        pi = PrefixPositionIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertSetEqual(set(pi.candidate_pairs("aefghijklmno")), {1})
        self.assertSetEqual(pi.cp_keys, {('a', 1)})

    def test_candidate_pairs_2(self):
        list_of_strings = ["bcdefghij", "abcdefghij", "cdefghijklm", "aefghijkluvw"]
        J = 0.9
        pi = PrefixPositionIndexing(list_of_strings, J)
        pi.make_many_to_one_index()
        self.assertSetEqual(set(pi.candidate_pairs("aefghijklmno")), {1, 3})
        self.assertSetEqual(pi.cp_keys, {('a', 1)})








if __name__ == '__main__':
    print('++++++++++++++++++++++++++++++++++++')
    unittest.main()
