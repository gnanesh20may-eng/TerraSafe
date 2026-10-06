package com.terrasafe.app.features.home

import android.content.Context
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.ContextCompat
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import org.maplibre.android.MapLibre
import org.maplibre.android.geometry.LatLng
import org.maplibre.android.maps.MapView
import org.maplibre.android.maps.Style

@Serializable
data class PlaceItem(
    val name_en: String,
    val name_ta: String,
    val lat: Double,
    val lon: Double,
    val type: String
)

@Serializable
data class PlacesData(
    val district_hqs: List<PlaceItem>,
    val hill_stations: List<PlaceItem>
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen() {
    val context = LocalContext.current
    var selectedPlace by remember { mutableStateOf<PlaceItem?>(null) }
    val sheetState = rememberModalBottomSheetState()
    var showSheet by remember { mutableStateOf(false) }

    val places = remember {
        try {
            val inputStream = context.assets.open("tamil_nadu_places.json")
            val jsonString = inputStream.bufferedReader().use { it.readText() }
            Json.decodeFromString<PlacesData>(jsonString)
        } catch (e: Exception) {
            PlacesData(emptyList(), emptyList())
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { ctx ->
                MapLibre.getInstance(ctx)
                MapView(ctx).apply {
                    onCreate(null)
                    getMapAsync { map ->
                        map.setStyle(Style.OUTDOORS) {
                            // Center on Tamil Nadu (~11.1271, 78.6569)
                            map.cameraPosition = org.maplibre.android.camera.CameraPosition.Builder()
                                .target(LatLng(11.1271, 78.6569))
                                .zoom(6.5)
                                .build()
                        }
                    }
                }
            }
        )

        // Overlay control or status
        Card(
            modifier = Modifier
                .align(Alignment.TopCenter)
                .padding(16.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Text(
                "Tamil Nadu: ${places.district_hqs.size} District HQs, ${places.hill_stations.size} Hill Stations",
                modifier = Modifier.padding(12.dp),
                style = MaterialTheme.typography.bodyMedium
            )
        }

        if (showSheet && selectedPlace != null) {
            ModalBottomSheet(
                onDismissRequest = { showSheet = false },
                sheetState = sheetState
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp)
                ) {
                    Text(selectedPlace?.name_en ?: "", style = MaterialTheme.typography.headlineSmall)
                    Text(selectedPlace?.name_ta ?: "", style = MaterialTheme.typography.titleMedium)
                    Spacer(Modifier.height(8.dp))
                    Text("Risk Level: WATCH (Score: 35/100)")
                    Text("Top Factor: Moderate rainfall accumulation")
                    Spacer(Modifier.height(16.dp))
                    Button(onClick = { showSheet = false }) {
                        Text("Open Evaluation")
                    }
                }
            }
        }
    }
}
