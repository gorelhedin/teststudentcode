from math import sqrt, floor, ceil
from itertools import islice, combinations
import numpy as np
from scipy.linalg import solve


class FactoriseBigInteger:
    """Class to Factorise BigIntegers"""

    class Utils:
        """Utils for Factorise Class"""
        @classmethod
        def element_appearances_in_array(cls, element, array):
            return len([None for e in array if element == e])

    @classmethod
    def calculate_r(cls, N, k, j):
        return int(sqrt(k*N)) + j

    @classmethod
    def is_prime(cls, n):
        if n <= 1:
            return False
        if n <= 3:
            return True
        if (n % 2 == 0) or (n % 3 == 0):
            # When multiple of 2 or 3, different behaviour
            return False
        i = 5
        while i <= ceil(sqrt(n)):
            if (n % i == 0) or (n % (i + 2) == 0):
                return False
            i = i + 6
        return True

    @classmethod
    def factorbase(cls, N, limit):
        def prime_generator(limit):
            n=1
            while n < limit:
                n += 1
                if cls.is_prime(n):
                    yield n
        return [x for x in islice(prime_generator(limit), N)]

    @classmethod
    def gcd(cls, a, b):  # Euclid's algorithm
        if a == 0:
            return 1
        if b == 0:
            return a
        elif a > b:
            return cls.gcd(b, a % b)
        else:
            return cls.gcd(b, a)

    @classmethod
    def factorise_small_number_in_range(cls, factorbase_set, factors, m, bot_limit=0):
        if m == 0:
            return
        for i, prime in enumerate(factorbase_set[bot_limit: ]):
            if m % prime == 0:
                cls.factorise_small_number_in_range(factorbase_set, factors, int(m / prime), bot_limit=i)
                break
        if prime != factorbase_set[-1]:
            factors.append(prime)


    @classmethod
    def transform_factorisation(cls, factorbase_set, set_of_primes):
        result = list()
        for f in reversed(factorbase_set):
            if cls.Utils.element_appearances_in_array(f, set_of_primes)%2 != 0:
                result.append(1)
            else:
                result.append(0)
        return list(reversed(result))

    @classmethod
    def build_matrix(cls, big_int_N, factorbase_set, L):
        solved = list()
        matrix = list()
        k = 2
        j = 2
        threshold = L
        while True:
            r_sqrt_mod_N_fact = list()
            r = cls.calculate_r(big_int_N, k, j)
            r_sqrt_mod_N = r**2 % big_int_N
            cls.factorise_small_number_in_range(factorbase_set, r_sqrt_mod_N_fact, r_sqrt_mod_N)
            if np.prod(r_sqrt_mod_N_fact) == r_sqrt_mod_N:
                matrix_candidate = cls.transform_factorisation(factorbase_set, r_sqrt_mod_N_fact)
                if (matrix_candidate not in matrix) and (sum(matrix_candidate) != 0):
                    print("FOUND LINE: {}".format((k, j)))
                    matrix.append(list(matrix_candidate))
                    persist_obj = {"r": r,
                                   "k": k,
                                   "j": j,
                                   "r_sqrt_mod_N_fact": r_sqrt_mod_N_fact,
                                   "representation": matrix_candidate}
                    solved.append(persist_obj)
            if len(matrix) == L:
                break
            k += 1
            if k%threshold == 0:
                j += 1
                if j%threshold == 0:
                    j = 2
                    threshold *= 2
                k = 2
        return solved, matrix

    @classmethod
    def brute_force_equation_system(cls, matrix, L, last=1, modK=2):
        """Solve binary systems with form xM=0.
        Where x, 0  are Vectors of size M and matrix is Matrix of size MxL.
        """
        print(L, "L")
        print(matrix.shape, "Shape")
        assert(isinstance(matrix, np.matrix))
        for i in range(last, 2**L):
            continue
            np_x = np.array(list(np.binary_repr(i).zfill(L))).astype(np.int8)
            np_x_per_M = np.squeeze(np.asarray(np_x.dot(matrix)))
            np_x_per_M_mod_K = np.remainder(np_x_per_M, modK)
            if not np.any(np_x_per_M_mod_K):
                return np_x, i
        return -1, -1

    @classmethod
    def solution(cls, solutions, x, N):
        left_build = list()
        right_build = list()
        for row in np.squeeze(np.nonzero(x)):
            line = solutions[row]
            left_build.append(line.get('r'))
            right_build.extend(line.get('r_sqrt_mod_N_fact'))
        left = np.prod(left_build) % N
        right = 1
        for val in right_build:
            right = (right*val) % N
        gcd = cls.gcd(abs(right-left), N)
        if gcd == 1:
            return False
        assert(cls.is_prime(gcd))
        return (gcd, int(N/gcd))


    @classmethod
    def find_solution(cls, solutions, matrix, L, N, i=0):
        while True:
            np_matrix = np.matrix(matrix)
            x, i = cls.brute_force_equation_system(np_matrix, L,  last=i+1)
            rows, cols = np_matrix.shape
            print(np_matrix.shape)
            """
            for matrix_combination in list(combinations(matrix, cols)):
                print(matrix_combination)
                try:
                    x = np.linalg.solve(np.matrix(matrix_combination), np.zeros(cols))
                    print(x)
                    break
                except np.linalg.LinAlgError as e:
                    print("error")
                    pass
            exit(1)
            print(x)
            exit(1)
            """
            solution = cls.solution(solutions, x, N)
            print(solution)
            if solution:
                break
        return solution


if __name__ == "__main__":
    BIG_INTEGER = 323
    BIG_INTEGER = 208863203872858491183629
    BIG_INTEGER = 307561
    BIG_INTEGER = 16637

    BIG_INTEGER = 208863203872858491183629
    M = 1000
    F = FactoriseBigInteger.factorbase(M, limit=int(sqrt(BIG_INTEGER)))
    L = len(F)+2
    solutions, matrix = FactoriseBigInteger.build_matrix(BIG_INTEGER, F, L)
    print(solutions)
    print(matrix)
    print(FactoriseBigInteger.find_solution(solutions, matrix, L, BIG_INTEGER))