#!/usr/bin/env python3
import unittest

from tools.editorial_link_graph_audit import analyze_graph, normalize_route, parse_main_links


class EditorialLinkGraphAuditTest(unittest.TestCase):
    def complete_graph(self):
        routes = {
            "/",
            "/guides/",
            "/guides/example/",
            "/characters/",
            "/characters/iris/",
            "/lab/",
            "/lab/example/",
        }
        graph = {
            "/": {"/guides/", "/characters/", "/lab/"},
            "/guides/": {"/guides/example/", "/"},
            "/guides/example/": {"/guides/", "/"},
            "/characters/": {"/characters/iris/", "/"},
            "/characters/iris/": {"/characters/", "/"},
            "/lab/": {"/lab/example/", "/"},
            "/lab/example/": {"/lab/", "/"},
        }
        return routes, graph

    def test_complete_graph_passes(self):
        routes, graph = self.complete_graph()
        result = analyze_graph(graph, expected_routes=routes, expected_page_count=len(routes))
        self.assertEqual(result["issues"], [])
        self.assertEqual(result["orphaned"], 0)
        self.assertEqual(result["unreachable"], 0)
        self.assertEqual(result["maxDepth"], 2)

    def test_orphan_and_missing_hub_child_fail(self):
        routes, graph = self.complete_graph()
        graph["/lab/"].remove("/lab/example/")
        graph["/lab/example/"] = set()
        result = analyze_graph(graph, expected_routes=routes, expected_page_count=len(routes))
        self.assertGreater(result["orphaned"], 0)
        self.assertTrue(any("does not directly link every child" in issue for issue in result["issues"]))

    def test_excessive_depth_fails(self):
        routes = {"/", "/one/", "/two/", "/three/", "/four/"}
        graph = {
            "/": {"/one/"},
            "/one/": {"/two/"},
            "/two/": {"/three/"},
            "/three/": {"/four/"},
            "/four/": {"/"},
        }
        result = analyze_graph(graph, expected_routes=routes, expected_page_count=len(routes))
        self.assertEqual(result["maxDepth"], 4)
        self.assertTrue(any("exceed home depth" in issue for issue in result["issues"]))

    def test_route_normalization_discards_fragment_and_query(self):
        self.assertEqual(normalize_route("https://lovetypes.tw/guides/example?x=1#part"), "/guides/example/")
        self.assertEqual(normalize_route("/#quiz-section"), "/")

    def test_external_url_with_matching_path_is_not_an_internal_edge(self):
        routes = {"/guides/example/"}
        raw = (
            '<main><a href="https://example.com/guides/example/">外站</a>'
            '<a href="https://lovetypes.tw/guides/example/">站內</a></main>'
        )
        targets, main_count = parse_main_links(raw, routes)
        self.assertEqual(main_count, 1)
        self.assertEqual(targets, {"/guides/example/"})


if __name__ == "__main__":
    unittest.main()
