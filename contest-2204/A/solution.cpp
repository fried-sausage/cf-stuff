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
        string s;
        cin >> n;
        cin >> s;
        int pos = s.find('L');
        // last character guaranteed to be 'L',
        // so no need for string::npos check
        cout << pos + 1 << '\n';
    }
    return 0;
}
