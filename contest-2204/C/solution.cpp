#include <bits/stdc++.h>

#define int int64_t

using namespace std;


int32_t main() {
    ios::sync_with_stdio(false);
    cin.tie(0);
    int t;
    cin >> t;
    while (t--) {
        int a, b, c, m;
        cin >> a >> b >> c >> m;
        int ab = lcm(a, b);
        int bc = lcm(b, c);
        int ca = lcm(c, a);
        int abc = lcm(ab, c);
        int all = m / abc;
        int only_a = m / a - m / ab - m / ca + all;
        int only_b = m / b - m / ab - m / bc + all;
        int only_c = m / c - m / ca - m / bc + all;
        int only_ab = m / ab - all;
        int only_bc = m / bc - all;
        int only_ca = m / ca - all;
        cout << only_a * 6 + only_ab * 3 + only_ca * 3 + all * 2 << ' ';
        cout << only_b * 6 + only_ab * 3 + only_bc * 3 + all * 2 << ' ';
        cout << only_c * 6 + only_bc * 3 + only_ca * 3 + all * 2 << '\n';
    }
    return 0;
}
