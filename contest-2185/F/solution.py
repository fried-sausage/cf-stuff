import sys


def main():
    buf = sys.stdin.buffer.read().split()

    curr = 0
    num_tests = int(buf[0])
    for _ in range(num_tests):
        n = int(buf[curr + 1])
        q = int(buf[curr + 2])
        curr += 2
        
        offset = ((1 << n) - 1)
        xor_tree = [0] * offset
        for i in range(1 << n):
            curr += 1
            xor_tree.append(int(buf[curr]))
        for i in range((1 << n) - 2, -1, -1):
            xor_tree[i] = xor_tree[(i << 1) + 1] ^ xor_tree[(i << 1) + 2]

        out = []
        for _ in range(q):
            cow_pos = int(buf[curr + 1]) - 1
            new_lvl = int(buf[curr + 2])
            curr += 2
            diff = new_lvl ^ xor_tree[offset + cow_pos]
            res = fight(n, xor_tree, cow_pos, diff)
            out.append(str(res))
        print("\n".join(out))


def fight(n, xor_tree, pos, skill_update):
    cows_above = 0
    start = 0
    xor_tree_pos = 0
    for k in range(n, 0, -1):
        half_size = 1 << (k - 1)
        mid = start + half_size
        l_xor = xor_tree[(xor_tree_pos << 1) + 1]
        r_xor = xor_tree[(xor_tree_pos << 1) + 2]
        if pos < mid:
            if (l_xor ^ skill_update) < r_xor:
                cows_above += half_size
            xor_tree_pos = (xor_tree_pos << 1) + 1
        else:
            if l_xor >= (r_xor ^ skill_update):
                cows_above += half_size
            xor_tree_pos = (xor_tree_pos << 1) + 2
            start = mid

    return cows_above


if __name__ == '__main__':
    main()
