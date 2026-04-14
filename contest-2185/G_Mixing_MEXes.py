import sys


def main():
    input = iter(sys.stdin.buffer.read().split())
    t = int(next(input))
    for _ in range(t):
        num_arrays = int(next(input))

        total_elements = 0
        total_freqs = {}

        sizes, mex1, mex2, s_after_remove = [], [], [], []

        for _ in range(num_arrays):
            size = int(next(input))

            counts = {}
            for _ in range(size):
                n = int(next(input))
                counts[n] = counts.get(n, 0) + 1
                total_freqs[n] = total_freqs.get(n, 0) + 1

            first_mex = 0
            while first_mex in counts:
                first_mex += 1

            second_mex = first_mex + 1
            while second_mex in counts:
                second_mex += 1

            sum_mex_after_removal = size * first_mex + sum(
                x - counts[x] * first_mex
                for x in range(first_mex)
                if x in counts and counts[x] == 1
            )
            
            total_elements += size
            sizes.append(size)
            mex1.append(first_mex)
            mex2.append(second_mex)
            s_after_remove.append(sum_mex_after_removal)

        ans = 0
        for i in range(num_arrays):
            size = sizes[i]

            # combinations not involving array i
            comb_not_touching_i = (total_elements - size) * (num_arrays - 2)
            ans += comb_not_touching_i * mex1[i]

            # removing from array i
            ans += s_after_remove[i] * (num_arrays - 1)

            # inserting into an array i
            ways_to_increment_mex = total_freqs.get(mex1[i], 0)
            ans += ways_to_increment_mex * mex2[i]

            ans += (total_elements - ways_to_increment_mex - size) * mex1[i]
        # out.append(ans)
        print(ans)
    # sys.stdout.write("\n".join(map(str, out)) + "\n")


if __name__ == "__main__":
    main()
