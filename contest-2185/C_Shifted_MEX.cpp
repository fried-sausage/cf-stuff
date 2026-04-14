#include <bits/stdc++.h>

#define int int64_t

using namespace std;

int longest_seq (const vector<int>& v) {
    if (v.empty()) return 0;

    int longest = 1, curr = 1;
    for (int i = 1; i < v.size(); i ++) {
        if (v[i - 1] == v[i]) continue;

        if (v[i - 1] + 1 == v[i]) {
            curr++;
        } else {
            curr = 1;
        }
        longest = max(longest, curr);
    }
    return longest;
}

int32_t main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);

    int ttt;
    for (cin >> ttt; ttt--; ) {
        int size;
        cin >> size;
        vector<int> v(size);
        for (int i=0; i < size; i++) cin >> v[i];
        sort(v.begin(), v.end());
        cout << longest_seq(v) << "\n";
    }
    return 0;
}
