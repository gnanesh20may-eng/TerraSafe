package com.terrasafe.domain

import java.util.PriorityQueue

data class Node(val id: String, val lat: Double, val lon: Double)
data class Edge(val toNodeId: String, val distanceKm: Double, val riskScore: Int, val isClosed: Boolean)

class RoutingEngine(private val nodes: Map<String, Node>, private val graph: Map<String, List<Edge>>) {
    fun findSafeRoute(startId: String, endId: String): List<String> {
        if (!nodes.containsKey(startId) || !nodes.containsKey(endId)) return emptyList()
        if (startId == endId) return listOf(startId)

        val distances = mutableMapOf<String, Double>().withDefault { Double.MAX_VALUE }
        val previous = mutableMapOf<String, String>()
        val pq = PriorityQueue<Pair<String, Double>>(compareBy { it.second })

        distances[startId] = 0.0
        pq.add(Pair(startId, 0.0))

        while (pq.isNotEmpty()) {
            val (current, currentDist) = pq.poll()
            if (current == endId) break
            if (currentDist > distances.getValue(current)) continue

            for (edge in graph[current] ?: emptyList()) {
                if (edge.isClosed || edge.riskScore >= 75) continue
                val weight = edge.distanceKm * (1.0 + edge.riskScore / 50.0)
                val newDist = currentDist + weight
                if (newDist < distances.getValue(edge.toNodeId)) {
                    distances[edge.toNodeId] = newDist
                    previous[edge.toNodeId] = current
                    pq.add(Pair(edge.toNodeId, newDist))
                }
            }
        }

        if (!previous.containsKey(endId) && startId != endId) return emptyList()

        val path = mutableListOf<String>()
        var curr: String? = endId
        while (curr != null) {
            path.add(0, curr)
            if (curr == startId) break
            curr = previous[curr]
        }

        return if (path.firstOrNull() == startId) path else emptyList()
    }
}
