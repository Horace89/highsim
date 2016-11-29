import math
import collections
import pprint
import re

import functools
from functools import cmp_to_key, reduce
from operator import or_
from itertools import count, takewhile



def pair(a, b):
    assert a != b
    return tuple(sorted((a, b)))

def order_symbol_1(symbol):
    """
    ordering key : corresponds ~to the ASCII value
    """
    assert isinstance(symbol, str) #Python has no 'char' type...
    return ord(symbol) - 96

def symbols(s, order=order_symbol_1):
    """
    see MMDS 3.9.2 "Representing Sets as Strings"
    removes duplicates in string s and orders the symbols according to order 'orde'
    """
    return tuple(sorted(set(s), key=order))

def id_and_symbols(s, order_symbol=order_symbol_1):
    return s, symbols(s, order=order_symbol)


identity = lambda x: x

def shingles_n(s, n, hashfun=identity):
    """Compute set of possible hashed n-shingles. """
    return {hashfun(s[i:i+n]) for i in range(len(s) - n + 1)}

def order_symbol_lex(shingle):
    """
    lexicographical order
    """
    #TEST
    assert isinstance(shingle, str)
    return shingle

def order_symbol_hash(shingle):
    """
    order based on the value of the hash of a shingle
    """
    return hash(shingle)

#Utility
def jaccard_sim(a, b):
    set_a, set_b = set(a), set(b)
    return float(len(set_a & set_b)) / len(set_a | set_b)

#shingle size is hardcoded
SHINGLE_SIZE = 3
shingles = functools.partial(shingles_n, n=SHINGLE_SIZE)
symbols_shingles = functools.partial(symbols, order=order_symbol_lex)

#function that takes a string, computes its shingles and returns the ordered set of symbols corresponding to these shingles (see MMDS p119, §2)
string_to_symbols = lambda s: symbols_shingles(shingles(s))


class PrefixIndexing(object):
    """
    MMDS 3.9.4
    """
    EPS = 1e-3
    def __init__(self, list_of_strings, J, order=order_symbol_1):
        self.list_of_strings = list_of_strings
        self.J = J
        self.order = order

        self.mode = "not_set"

    def prefix_length(self, s):
        assert len(s), "string {} has zero length !".format(s)
        return math.floor((1-self.J) * len(s) + self.EPS) + 1

    def prefix(self, s):
        """
        computes the prefix of the set that represents string s
        depends on the chosen ordering
        see MMDS §3.26 for details and example
        """
        return symbols(s, order=self.order)[:self.prefix_length(s)]

    def make_many_to_one_index(self):
        """
        see 1st paragraph, MMDS page 121.
        """
        self.mode = "many_to_one"

        ii = {}
        for indx_s, s in enumerate(self.list_of_strings):
            for symbol in self.prefix(s):
                ii.setdefault(symbol, set()).add(indx_s)
        self.ii = ii

    def candidate_pairs(self, s):
        """
        in the many-one problem, returns the candidate strings in the index that may match string s
        requirement: the many-one index must have been computed first.
        """
        assert self.mode == "many_to_one"
        cp_keys = self.prefix(s) & self.ii.keys()

        #for unittest
        self.cp_keys = cp_keys

        return self.fusion_values(cp_keys)

    def fusion_values(self, keys):
        """
        utility

        if keys = [a,b]
        ==> ii[a] U ii[b]
        """
        return reduce(or_, (self.ii[k] for k in keys), set())

    def make_many_to_many_index(self):
        """
        see 2nd paragraph, MMDS page 121.
        """
        self.mode = "many_to_many"

        cp = set()  #candidate pairs
        ii = {}
        for indx_s, s in enumerate(self.list_of_strings):
            for symbol in self.prefix(s):
                if symbol in ii:
                    cp |= set(pair(indx_s, indx_t) for indx_t in ii[symbol])
                    #print("{} to be compared with: {}".format(s, list(map(self.indx_to_string, ii[symbol]))))
                ii.setdefault(symbol, set()).add(indx_s)

        self.ii = ii
        return cp

    def indx_to_string(self, indx):
        return self.list_of_strings[indx]

    def display(self, display_strings=False):
        print("inner list_of_strings:", self.list_of_strings)
        print("ii (indices):")

        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(self.ii)

        if display_strings:
            print("\nii (strings):")
            for k in self.ii:
                print("  {}: {}".format(k, set(map(self.indx_to_string, self.ii[k]))))
            print()


class PrefixPositionIndexing(PrefixIndexing):
    """
    MMDS 3.9.5
    """
    def __init__(self, list_of_strings, J, order=order_symbol_1):
        super().__init__(list_of_strings, J, order=order)

    def make_many_to_one_index(self):
        """
        see 1st paragraph, MMDS page 121.
        """
        self.mode = "many_to_one"

        ii = {}
        for indx_s, s in enumerate(self.list_of_strings):
            for i, symbol in enumerate(self.prefix(s), 1):
                ii.setdefault((symbol, i), set()).add(indx_s)
        self.ii = ii

    def max_j(self, i, s):
        J = self.J
        return math.floor((len(s) * (1-J) - i + 1 + J)/J + self.EPS)

    def candidate_pairs(self, s):
        """
        in the many-one problem, returns the candidate strings in the index that may match string s
        requirement: the many-one index must have been computed first.
        """
        assert self.mode == "many_to_one"

        cp_keys = set()
        for i, symbol in enumerate(self.prefix(s), 1):
        #print("cp_keys:", cp_keys)
            potential_keys = [(symbol, j) for j in range(1, self.max_j(i, s) + 1)]
            #print("potential_keys:", potential_keys)
            cp_keys |= potential_keys & self.ii.keys()

        #for unittest
        self.cp_keys = cp_keys

        #print("cp_keys:", cp_keys)
        #no need to sort but better for reading
        return sorted(self.fusion_values(cp_keys))

    def make_many_to_many_index(self):
        """
        see 2nd paragraph, MMDS page 121.
        """
        self.mode = "many_to_many"

        self.ii = {}
        ii = self.ii

        cp = set()
        for indx_s, s in enumerate(self.list_of_strings):
            #print("\n- considered string:", (indx_s, s))

            #we iterate over list_of_strings
            c_keys_for_s = set()
            #print("ii.keys:", ii.keys())

            prefixes = list(enumerate(self.prefix(s), 1))
            for i, symbol in prefixes:
                #print("self.max_j({}, {}): {}".format(i, s, self.max_j(i, s)))
                potential_keys = [(symbol, j) for j in range(1, self.max_j(i, s) + 1)]
                #print("for {}, {}, the potential keys are {}".format(s, i, potential_keys))
                c_keys_for_s |= potential_keys & ii.keys()
                #print("thus we add to c_keys_for_s:", potential_keys & ii.keys())

            #print("c_keys_for_s final:", c_keys_for_s)
            c_for_s = self.fusion_values(c_keys_for_s)
            #print("cp for s:", self.fusion_values(c_keys_for_s))
            cp |= set(pair(indx_s, indx_t) for indx_t in c_for_s)

            #print("We add s to the keys", prefixes)
            #maintenant qu'on a fini de regarder les candidats pour s, on rajoute s à ii
            for i, symbol in prefixes:
                ii.setdefault((symbol, i), set()).add(indx_s)
            #print("ii:", ii)

        return sorted(cp) #no need to sort but better for reading


class PrefixPositionLengthIndexing(PrefixIndexing):
    """
    3.9.6
    """
    def __init__(self, list_of_strings, J, order=order_symbol_1):
        super().__init__(list_of_strings, J, order=order)

    def make_many_to_one_index(self):
        self.mode = "many_to_one"

        ii = {}
        for indx_s, s in enumerate(self.list_of_strings):
            for i, symbol in enumerate(self.prefix(s), 1):
                ii.setdefault((symbol, i, len(s) - i), set()).add(indx_s)
        self.ii = ii


    def candidate_pairs(self, s):
        """
        in the many-one problem, returns the candidate strings in the index that may match string s
        requirement: the many-one index must have been computed first.
        """
        assert self.mode == "many_to_one"

        potential_keys_inf, potential_keys_sup = set(), set()
        prefixes = list(enumerate(self.prefix(s), 1))

        #case p >= q
        for i, symbol in prefixes:
            p = len(s) - i
            for q in range(p, -1, -1):
                assert q != -1
                no_j_for_this_q = True
                for j in takewhile(lambda j: (q + 1) >= self.J * (len(s) + j - 1), count(1)):
                    no_j_for_this_q = False
                    potential_keys_inf.add((symbol, j, q))

                #print("i:{}, q:{}, j:{}".format(i, q, j_for_q))
                if no_j_for_this_q:
                    break
        #print("potential_keys_inf:", potential_keys_inf)

        #case p < q
        for i, symbol in prefixes:
            p = len(s) - i
            for q in count(p + 1):
                no_j_for_this_q = True
                for j in takewhile(lambda j: (len(s) - i + 1 + self.EPS) >= (self.J * (i + j - 1 + q)), count(1)):
                    no_j_for_this_q = False
                    potential_keys_sup.add((symbol, j, q))

                #print("i:{}, q:{}, j:{}".format(i, q, j_for_q))
                if no_j_for_this_q:
                    break
        #print("potential_keys_sup:", potential_keys_sup)

        #print("potential_keys:", potential_keys_inf | potential_keys_sup)

        cp_keys = (potential_keys_inf | potential_keys_sup) & self.ii.keys()

        #print("cp_keys:", cp_keys)
        return sorted(self.fusion_values(cp_keys)) #no need to sort but better for reading


    def make_many_to_many_index(self, return_sorted=False):
        """
        see 2nd paragraph, MMDS page 121.
        """
        self.mode = "many_to_many"

        self.ii = {}
        ii = self.ii

        cp = set()

        potential_keys_inf, potential_keys_sup = set(), set()

        for indx_s, s in enumerate(self.list_of_strings):
            potential_keys_inf.clear()
            potential_keys_sup.clear()

            prefixes = list(enumerate(self.prefix(s), 1))

            #case p >= q
            for i, symbol in prefixes:
                p = len(s) - i
                for q in range(p, -1, -1):
                    assert q != -1
                    no_j_for_this_q = True
                    for j in takewhile(lambda j: (q + 1) >= self.J * (len(s) + j - 1), count(1)):
                        no_j_for_this_q = False
                        potential_keys_inf.add((symbol, j, q))

                    if no_j_for_this_q:
                        break
            #print("potential_keys_inf:", potential_keys_inf)

            #case p < q
            for i, symbol in prefixes:
                p = len(s) - i
                for q in count(p + 1):
                    no_j_for_this_q = True

                    for j in takewhile(lambda j: (len(s) - i + 1 + self.EPS) >= (self.J * (i + j - 1 + q)), count(1)):
                        no_j_for_this_q = False
                        potential_keys_sup.add((symbol, j, q))

                    if no_j_for_this_q:
                        break
            #print("potential_keys_sup:", potential_keys_sup)
            #print("potential_keys:", potential_keys_inf | potential_keys_sup)

            c_keys_for_s = (potential_keys_inf | potential_keys_sup) & ii.keys()

            #print("c_keys_for_s:", c_keys_for_s)
            c_for_s = self.fusion_values(c_keys_for_s)
            cp |= set(pair(indx_s, indx_t) for indx_t in c_for_s)

            #print("We add s (n°{}) to keys {}".format(indx_s, prefixes))

            #We add s to ii
            for i, symbol in prefixes:
                ii.setdefault((symbol, i, len(s) - i), set()).add(indx_s)
            #print("ii:", ii)

        return sorted(cp) if return_sorted else cp


if __name__ == '__main__':

    print("\n+++ A) PrefixIndexing +++")
    print("*** TESTING of the many-one problem ***")
    list_of_strings = ["bcdefghij", "abcdefghij", "cdefghijklm", "aefghijkluvw"]
    JACCARD_SIM_THRESHOLD = 0.9

    pi = PrefixIndexing(list_of_strings, JACCARD_SIM_THRESHOLD)
    pi.make_many_to_one_index()
    #pi.display(display_strings=True)

    for probe_string in ("aefghijklmno", "defghijklmno"):
        print("candidate strings for '{}': {}".format(probe_string, pi.candidate_pairs(probe_string)))

    print("*** TESTING of the many-many problem ***")
    list_of_strings = ["bcdefghij", "abcdefghij", "abcdefghvwxyz", "cdefghijklm", "aefghijkluvw", "cdefghlmnopq"]
    JACCARD_SIM_THRESHOLD = 0.9

    pi2 = PrefixIndexing(list_of_strings, JACCARD_SIM_THRESHOLD)
    cpmm = pi2.make_many_to_many_index()
    print("candidate pairs (many-many):", cpmm)




    print("\n+++ B) PrefixPositionIndexing +++")
    print("*** TESTING of the many-one problem ***")
    list_of_strings = ["bcdefghij", "abcdefghij", "cdefghijklm", "aefghijkluvw"]
    JACCARD_SIM_THRESHOLD = 0.9
    ppi = PrefixPositionIndexing(list_of_strings, JACCARD_SIM_THRESHOLD)

    ppi.make_many_to_one_index()
    #ppi.display()
    #print("cp3:", ppi.candidate_pairs("acdefghijk"))
    for probe_string in ("acdefghijk", "defghijklmno"):
        print("candidate strings for '{}': {}".format(probe_string, ppi.candidate_pairs(probe_string)))


    print("*** TESTING of the many-many problem ***")
    #list_of_strings = ["bcdefghij", "abcdefghij", "cdefghijklm", "aefghijkluvw"]
    #list_of_strings = ["bcdefghij", "abcdefghij", "ef", "cdefghijklm", "aefghijkluvw", "aefghijlmnopq"]
    list_of_strings = ["bcdefghij", "cd", "abcdefghij", "bcdefghijmno", "cdefghijklm", "aefghijkluvw", "aefghijlmnopq"]

    JACCARD_SIM_THRESHOLD = 0.9
    ppi = PrefixPositionIndexing(list_of_strings, JACCARD_SIM_THRESHOLD)
    cpmm = ppi.make_many_to_many_index()
    #print("\n\n")
    #ppi.display()
    print("candidate pairs (many-many):", cpmm)





    print("\n+++ C) PrefixPositionLengthIndexing +++")
    print("*** TESTING of the many-one problem ***")
    list_of_strings = ["bcdefghij", "cd", "abcdefghij", "bcdefghijmno"]
    JACCARD_SIM_THRESHOLD = 0.8
    ppli = PrefixPositionLengthIndexing(list_of_strings, JACCARD_SIM_THRESHOLD)
    ppli.make_many_to_one_index()
    #print("\n\n")
    #ppli.display()
    for probe_string in ("acdefghijk", "bcdefghijmno"):
        print("candidate strings for '{}': {}".format(probe_string, ppli.candidate_pairs(probe_string)))

    print("*** TESTING of the many-many problem ***")
    list_of_strings = ["bcdefghij", "cd", "abcdefghij", "bcdefghijmno", "cdefghijklm", "aefghijkluvw", "aefghijlmnopq"]

    JACCARD_SIM_THRESHOLD = 0.9
    ppli = PrefixPositionLengthIndexing(list_of_strings, JACCARD_SIM_THRESHOLD)
    cpmm = ppli.make_many_to_many_index()
    #print("\n\n")
    #ppi.display()
    print("candidate pairs (many-many):", cpmm)


    print("\n** THE END **\n")
