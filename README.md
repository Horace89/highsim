This Python code provides an implementation of the three algorithms found in §3.9 "Methods for High Degrees of Similarity" of the fantastic book Mining of Massive Datasets [1]. 

Type `python simil.py` for a sample run. Unit tests are also provided in mytests.py.

When we want to find sets that are almost identical, there are methods that can be faster than minhashing and LSH (exposed in [1, §3]). Moreover, these methods are exact, in that they find every pair of items with the desired degree of similarity. There are no false negatives, as there can be with LSH.

1. Character Indexes (see class `PrefixIndexing`): If we represent sets by strings, and the similarity threshold is close to 1, we can index all strings by their first few characters. The prefix whose characters must be indexed is approximately the length of the string times the maximum Jaccard distance (1 minus the minimum Jaccard similarity).

2. Position Indexes (see class `PrefixPositionIndexing`): We can index strings not only on the characters in their prefixes, but on the position of that character within the prefix. We reduce the number of pairs of strings that must be compared, because if two strings share a character that is not in the first position in both strings, then we know that either there are some preceding characters that are in the union but not the intersection, or there is an earlier symbol that
appears in both strings.

3. Suffix Indexes (see class `PrefixPositionLengthIndexing`): We can also index strings based not only on the characters in their prefixes and the positions of those characters, but on the length of the character’s suffix – the number of positions that follow it in the string. This structure further reduces the number of pairs that must be compared, because a common symbol with different suffix lengths implies additional characters that must be in the union but not in the intersection.


[1] Mining of Massive Datasets.
Jure Leskovec, Anand Rajaraman, Jeff Ullman.
Available at http://www.mmds.org/
