#include <bits/stdc++.h>

#define int int64_t

using namespace std;


int32_t main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);
    int t;
    cin >> t;
    while (t--) {
        int n, i;
        char c;
        cin >> n;
        for (i = 0; i < n && cin >> c && c != 'L'; i++) ;
        cout << i + 1 << '\n';
        for (++i; i < n && cin >> c; i++) ;
    }
    return 0;
}
