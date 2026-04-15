#include <bits/stdc++.h>

#define int int64_t

using namespace std;


int32_t main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);
    int t;
    cin >> t;
    while (t--) {
        int n;
        cin >> n;
        int ops = 0;
        int prev_max = 0;
        while (n--) {
            int curr;
            cin >> curr;
            if (prev_max <= curr) {
                ++ops;
                prev_max = curr;
            }
        }
        cout << ops << '\n'; 
    }
    return 0;
}
