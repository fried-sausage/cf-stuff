#include <bits/stdc++.h>

#define int int64_t
#define NOT_VISITED (-1)

using namespace std;


struct ComponentInfo {
    int count0 = 0;
    int count1 = 0;
    bool is_bipartite = true;
};


void update_inplace_with(
    struct ComponentInfo &self,
    const struct ComponentInfo &other
) {
    self.count0 += other.count0;
    self.count1 += other.count1;
    self.is_bipartite = self.is_bipartite && other.is_bipartite;
}


struct ComponentInfo dfs(
    int v_curr, const vector<vector<int>> &adj, vector<int> &color
) {
    struct ComponentInfo retval{0, 0, true};
    retval.count0 = (color[v_curr] == 0);
    retval.count1 = (color[v_curr] == 1);
    for (int v_next : adj[v_curr]) {
        if (color[v_next] == NOT_VISITED) {
            color[v_next] = color[v_curr] ^ 1;
            auto child = dfs(v_next, adj, color);
            update_inplace_with(retval, child);
        } else if (color[v_next] == color[v_curr]) {
            retval.is_bipartite = false;
        }
    }
    return retval;
}


int32_t main() {
    ios_base::sync_with_stdio(false);
    cin.tie(0);
    int t;
    cin >> t;
    while (t--) {
        int vertices, edges;
        cin >> vertices >> edges;
        vector<int> color(vertices + 1, NOT_VISITED);
        vector<vector<int>> adj(vertices + 1);
        for (int i = 0; i < edges; ++i) {
            int v1, v2;
            cin >> v1 >> v2;
            adj[v1].push_back(v2);
            adj[v2].push_back(v1);
        }
        int ans = 0;
        for (int v = 1; v <= vertices; ++v) {
            if (color[v] != NOT_VISITED) continue;
            color[v] = 0;
            struct ComponentInfo res = dfs(v, adj, color);
            if (res.is_bipartite) {
                ans += max(res.count0, res.count1);
            }
        }
        cout << ans << '\n';
    }
    return 0;
}
