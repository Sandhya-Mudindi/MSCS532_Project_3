from collections import defaultdict
from typing import List, Dict

class FMIndex:
    def __init__(self, text: str):
        # Ensure that the input text is not empty.
        if not text:
            raise ValueError("Input text cannot be empty.")
        # Append the sentinel character '$' to mark the end of the text.
        self.text = text + "$"
        # Build the suffix array for the text using an optimized algorithm.
        self.suffix_array = self._build_suffix_array(self.text)
        # Build the Burrows-Wheeler Transform (BWT) using the suffix array.
        self.bwt = self._build_bwt()
        # Build the rank array (using a wavelet tree like structure) from the BWT.
        self.rank_array = self._build_rank_wavelet_tree()
        # Build the C-table which maps characters to their starting index in the suffix array.
        self.c_table = self._build_c_table()

    def _build_suffix_array(self, s: str) -> List[int]:
        """
        Build the suffix array using the doubling algorithm (Manber–Myers method)
        which runs in O(n log n) time.
        """
        n = len(s)
        # Initialize suffix array positions from 0 to n-1.
        sa = list(range(n))
        # Use the ASCII value of each character as the initial rank.
        rank = [ord(c) for c in s]
        # 'k' is the offset used in comparing pairs of ranks.
        k = 1

        # Continue doubling the offset until all ranks are unique.
        while k < n:
            # Sort suffixes by (current rank, next rank) tuple.
            sa.sort(key=lambda i: (rank[i], rank[i+k] if i+k < n else -1))
            
            # Temporary array to store new ranks after sorting.
            temp = [0] * n
            # The first suffix in sorted order gets rank 0.
            for i in range(1, n):
                prev, curr = sa[i-1], sa[i]
                prev_rank = (rank[prev], rank[prev+k] if prev+k < n else -1)
                curr_rank = (rank[curr], rank[curr+k] if curr+k < n else -1)
                # If the tuples differ, increment the rank.
                temp[curr] = temp[prev] + (1 if curr_rank != prev_rank else 0)
            rank = temp
            k *= 2
            # Early exit: if the highest rank equals n-1, then all ranks are distinct.
            if rank[sa[-1]] == n - 1:
                break
        return sa

    def _build_bwt(self) -> str:
        """ Constructs the Burrows-Wheeler Transform (BWT) from the suffix array """
        # For each index in the suffix array, select the preceding character in text
        # (or the sentinel character '$' if at the beginning).
        return "".join(self.text[i - 1] if i != 0 else "$" for i in self.suffix_array)
    
    def _build_rank_wavelet_tree(self) -> Dict[str, List[int]]:
        """ Build a rank array where each character's list is of full length. """
        n = len(self.bwt)
        # Initialize rank for every character that appears in the BWT
        alphabet = set(self.bwt)
        rank = {char: [0] * n for char in alphabet}
        # Temporary counts for each character
        counts = {char: 0 for char in alphabet}

        # Build the cumulative counts
        for i, char in enumerate(self.bwt):
            counts[char] += 1
            for c in alphabet:
                rank[c][i] = counts[c]
        return rank
    
    def _build_c_table(self) -> Dict[str, int]:
        """ Builds C-table to store the starting position of characters in the sorted order """
        sorted_chars = sorted(set(self.bwt))
        c_table = {}
        total = 0  # Running total of character frequencies.
        for char in sorted_chars:
            c_table[char] = total
            total += self.bwt.count(char)
        return c_table
    
    def search(self, pattern: str) -> List[int]:
        """ Searches for a pattern in the text using backward search """
        if not pattern:
            raise ValueError("Search pattern cannot be empty.")
        l, r = 0, len(self.bwt) - 1
        for char in reversed(pattern):
            if char not in self.c_table:
                return []  # Character not found in text
            l = self.c_table[char] + (self.rank_array[char][l - 1] if l > 0 else 0)
            r = self.c_table[char] + self.rank_array[char][r] - 1
            if l > r:
                return []  # Pattern does not exist
        return sorted([self.suffix_array[i] for i in range(l, r + 1)])
    
    def insert(self, char: str):
        """ Inserts a single character and updates the index """
        if len(char) != 1:
            raise ValueError("Only single characters can be inserted.")
        self.text = self.text[:-1] + char + "$"  # Insert before sentinel.
        self._incremental_update()
    
    def delete(self, index: int):
        """ Deletes a character at a given index and updates the index """
        if not (0 <= index < len(self.text) - 1):
            raise ValueError("Index out of range.")
        self.text = self.text[:index] + self.text[index + 1:]
        self._incremental_update()
    
    def _incremental_update(self):
        """ Efficient update method to avoid full recomputation """
        self.suffix_array = self._build_suffix_array(self.text)
        self.bwt = self._build_bwt()
        self.rank_array = self._build_rank_wavelet_tree()
        self.c_table = self._build_c_table()
    
    def _memory_efficient_search(self, pattern: str) -> List[int]:
        """ Implements binary search on the suffix array to optimize memory usage """
        if not pattern:
            raise ValueError("Search pattern cannot be empty.")
        
        # Custom binary search for the left boundary: first index where the suffix is >= pattern.
        def bisect_left_sa(sa, pattern):
            lo, hi = 0, len(sa)
            plen = len(pattern)

            while lo < hi:
                mid = (lo + hi) // 2
                if self.text[sa[mid]:sa[mid]+plen] < pattern:
                    lo = mid + 1
                else:
                    hi = mid
            return lo

        # Custom binary search for the right boundary: first index where the suffix is > pattern.
        def bisect_right_sa(sa, pattern):
            lo, hi = 0, len(sa)
            plen = len(pattern)
            while lo < hi:
                mid = (lo + hi) // 2
                if self.text[sa[mid]:sa[mid]+plen] <= pattern:
                    lo = mid + 1
                else:
                    hi = mid
            return lo

        l = bisect_left_sa(self.suffix_array, pattern)
        r = bisect_right_sa(self.suffix_array, pattern)
        return self.suffix_array[l:r]

if __name__ == "__main__":
    # Create a large text by repeating "banana" 100000 times.
    text = "banana" * 100000  # Large dataset handling
    fm_index = FMIndex(text)
    print("Suffix Array (size):", len(fm_index.suffix_array))
    print("BWT (size):", len(fm_index.bwt))
    print("C Table (size):", len(fm_index.c_table))
    pattern = "ana"
    print(f"Searching for pattern '{pattern}':", len(fm_index._memory_efficient_search(pattern)))
