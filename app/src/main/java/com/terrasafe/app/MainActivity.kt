package com.terrasafe.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.*
import com.terrasafe.app.ui.theme.TerraSafeTheme
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object Home : Screen("home", "Home", Icons.Default.Home)
    object Evaluation : Screen("evaluation", "Evaluation", Icons.Default.Assessment)
    object Rescue : Screen("rescue", "Rescue Hub", Icons.Default.Security)
    object Alerts : Screen("alerts", "Alerts", Icons.Default.Notifications)
    object Places : Screen("places", "My Places", Icons.Default.Place)
    object Settings : Screen("settings", "Settings", Icons.Default.Settings)
    object About : Screen("about", "About", Icons.Default.Info)
}

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TerraSafeTheme {
                MainScreen()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    val items = listOf(Screen.Home, Screen.Evaluation,Screen.Rescue, Screen.Alerts, Screen.Places)

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet {
                Spacer(Modifier.height(16.dp))
                Text("TerraSafe Navigation", modifier = Modifier.padding(16.dp), style = MaterialTheme.typography.titleLarge)
                HorizontalDivider()
                NavigationDrawerItem(
                    label = { Text("Settings") },
                    selected = false,
                    icon = { Icon(Screen.Settings.icon, null) },
                    onClick = {
                        scope.launch { drawerState.close() }
                        navController.navigate(Screen.Settings.route)
                    }
                )
                NavigationDrawerItem(
                    label = { Text("About") },
                    selected = false,
                    icon = { Icon(Screen.About.icon, null) },
                    onClick = {
                        scope.launch { drawerState.close() }
                        navController.navigate(Screen.About.route)
                    }
                )
            }
        }
    ) {
        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text("TerraSafe • Tamil Nadu") },
                    navigationIcon = {
                        IconButton(onClick = { scope.launch { drawerState.open() } }) {
                            Icon(Icons.Default.Menu, contentDescription = "Menu")
                        }
                    },
                    actions = {
                        IconButton(onClick = { navController.navigate(Screen.Alerts.route) }) {
                            Icon(Icons.Default.Notifications, contentDescription = "Alerts")
                        }
                    }
                )
            },
            bottomBar = {
                NavigationBar {
                    val navBackStackEntry by navController.currentBackStackEntryAsState()
                    val currentRoute = navBackStackEntry?.destination?.route
                    items.forEach { screen ->
                        NavigationBarItem(
                            icon = { Icon(screen.icon, contentDescription = screen.title) },
                            label = { Text(screen.title) },
                            selected = currentRoute == screen.route,
                            onClick = {
                                navController.navigate(screen.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        )
                    }
                }
            }
        ) { innerPadding ->
            NavHost(
                navController = navController,
                startDestination = Screen.Home.route,
                modifier = Modifier.padding(innerPadding)
            ) {
                composable(Screen.Home.route) { HomeScreen() }
                composable(Screen.Evaluation.route) { EvaluationScreen() }
                composable(Screen.Rescue.route) { RescueHubScreen() }
                composable(Screen.Alerts.route) { AlertsScreen() }
                composable(Screen.Places.route) { PlacesScreen() }
                composable(Screen.Settings.route) { SettingsScreen() }
                composable(Screen.About.route) { AboutScreen() }
            }
        }
    }
}

// Placeholder screens for 7 navigation targets
@Composable fun HomeScreen() { Box(Modifier.fillMaxSize(), contentAlignment = androidx.compose.ui.Alignment.Center) { Text("Home Screen: 3D Tamil Nadu Map (38 District HQs & 18 Hill Stations)") } }
@Composable fun EvaluationScreen() { Box(Modifier.fillMaxSize(), contentAlignment = androidx.compose.ui.Alignment.Center) { Text("Evaluation Screen: Risk Levels, What-If Slider, False-Alarm Rule") } }
@Composable fun RescueHubScreen() { Box(Modifier.fillMaxSize(), contentAlignment = androidx.compose.ui.Alignment.Center) { Text("Rescue Hub Screen: Connected People, SOS Queue, Triage & Family Flow") } }
@Composable fun AlertsScreen() { Box(Modifier.fillMaxSize(), contentAlignment = androidx.compose.ui.Alignment.Center) { Text("Alerts Screen: State Machine (NEW, ACK, ACTIVE, RESOLVED) & Hash-Chain Audit") } }
@Composable fun PlacesScreen() { Box(Modifier.fillMaxSize(), contentAlignment = androidx.compose.ui.Alignment.Center) { Text("My Places Screen: Saved Locations & Thresholds") } }
@Composable fun SettingsScreen() { Box(Modifier.fillMaxSize(), contentAlignment = androidx.compose.ui.Alignment.Center) { Text("Settings Screen: Language, Voice, Offline Maps, Backend URL") } }
@Composable fun AboutScreen() { Box(Modifier.fillMaxSize(), contentAlignment = androidx.compose.ui.Alignment.Center) { Text("About Screen: Version, Data Sources, Safety Disclaimer") } }
