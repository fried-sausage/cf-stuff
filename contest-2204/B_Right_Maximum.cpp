#include <bits/stdc++.h>

#define int int64_t

using namespace std;


int solve(int n, int prev_max, int acc) {
    if (n == 0) return acc;
    int curr;
    cin >> curr;
    if (prev_max <= curr) {
        prev_max = curr;
        ++acc;
    }
    return solve(n - 1, prev_max, acc);
}


int32_t main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);
    int t;
    cin >> t;
    while (t--) {
        int n;
        cin >> n;
        cout << solve(n, 0, 0) << '\n';
    }
    return 0;
}
