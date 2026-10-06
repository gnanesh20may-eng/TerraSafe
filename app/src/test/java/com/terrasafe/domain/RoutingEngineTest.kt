package com.terrasafe.domain

import org.junit.Assert.*
import org.junit.Test

class RoutingEngineTest {
    @Test
    fun testStartEqualsEnd() {
        val nodes = mapOf("A" to Node("A", 0.0, 0.0))
        val engine = RoutingEngine(nodes, emptyMap())
        val path = engine.findSafeRoute("A", "A")
        assertEquals(listOf("A"), path)
    }

    @Test
    fun testShortestSafePath() {
        val nodes = mapOf(
            "A" to Node("A", 0.0, 0.0),
            "B" to Node("B", 1.0, 1.0),
            "C" to Node("C", 2.0, 2.0)
        )
        val graph = mapOf(
            "A" to listOf(Edge("B", 1.0, 10, false), Edge("C", 5.0, 10, false)),
            "B" to listOf(Edge("C", 1.0, 10, false)),
            "C" to emptyList()
        )
        val engine = RoutingEngine(nodes, graph)
        val path = engine.findSafeRoute("A", "C")
        assertEquals(listOf("A", "B", "C"), path)
    }

    @Test
    fun testAvoidClosedAndCriticalEdges() {
        val nodes = mapOf(
            "A" to Node("A", 0.0, 0.0),
            "B" to Node("B", 1.0, 1.0),
            "C" to Node("C", 2.0, 2.0)
        )
        val graph = mapOf(
            "A" to listOf(Edge("B", 1.0, 80, false), Edge("C", 3.0, 10, false)), // B is critical (80)
            "B" to listOf(Edge("C", 1.0, 10, false)),
            "C" to emptyList()
        )
        val engine = RoutingEngine(nodes, graph)
        val path = engine.findSafeRoute("A", "C")
        assertEquals(listOf("A", "C"), path) // Avoided B because risk >= 75
    }

    @Test
    fun testUnreachableDestination() {
        val nodes = mapOf(
            "A" to Node("A", 0.0, 0.0),
            "B" to Node("B", 1.0, 1.0)
        )
        val engine = RoutingEngine(nodes, emptyMap())
        val path = engine.findSafeRoute("A", "B")
        assertTrue(path.isEmpty())
    }
}
