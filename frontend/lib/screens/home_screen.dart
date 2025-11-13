import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/websocket_service.dart';
import '../services/api_service.dart';
import '../widgets/process_card.dart';
import '../widgets/resource_card.dart';
import '../widgets/prediction_panel.dart';
import '../widgets/graph_painter.dart';
import '../widgets/scenario_selector.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _showScenarios = false;
  int _connectionAttempts = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _connectToBackend();
    });
  }

  void _connectToBackend() {
    final wsService = Provider.of<WebSocketService>(context, listen: false);
    wsService.connect();

    Future.delayed(const Duration(seconds: 3), () {
      if (!wsService.isConnected && _connectionAttempts < 3) {
        _connectionAttempts++;
        print('Reconnecting... Attempt $_connectionAttempts');
        _connectToBackend();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Deadlock Detection System'),
        actions: [
          Consumer<WebSocketService>(
            builder: (context, wsService, child) {
              return Row(
                children: [
                  Icon(
                    wsService.isConnected ? Icons.cloud_done : Icons.cloud_off,
                    color: wsService.isConnected ? Colors.green : Colors.red,
                  ),
                  const SizedBox(width: 8),
                  Text(wsService.isConnected ? 'Connected' : 'Disconnected'),
                  const SizedBox(width: 16),
                ],
              );
            },
          ),
          IconButton(
            icon: Icon(_showScenarios ? Icons.close : Icons.science),
            tooltip: _showScenarios ? 'Hide Scenarios' : 'Show Test Scenarios',
            onPressed: () {
              setState(() {
                _showScenarios = !_showScenarios;
              });
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () async {
              try {
                await Provider.of<ApiService>(context, listen: false).resetSystem();
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('System reset successfully')),
                  );
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: $e')),
                  );
                }
              }
            },
          ),
        ],
      ),
      body: Consumer<WebSocketService>(
        builder: (context, wsService, child) {
          if (!wsService.isConnected) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 20),
                  const Text(
                    'Connecting to backend...',
                    style: TextStyle(fontSize: 18),
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    'Make sure backend is running on http://127.0.0.1:8000',
                    style: TextStyle(fontSize: 14, color: Colors.grey),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: () {
                      _connectionAttempts = 0;
                      _connectToBackend();
                    },
                    child: const Text('Retry Connection'),
                  ),
                ],
              ),
            );
          }

          final systemState = wsService.systemState;
          if (systemState == null) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 20),
                  Text('Waiting for data...'),
                ],
              ),
            );
          }

          return Stack(
            children: [
              Row(
                children: [
                  // Left Panel - Controls
                  Expanded(
                    flex: 1,
                    child: _buildControlPanel(context, systemState),
                  ),

                  // Center Panel - Visualization
                  Expanded(
                    flex: 2,
                    child: GraphVisualization(graphData: systemState['graph'] ?? {}),
                  ),

                  // Right Panel - Stats & Prediction
                  Expanded(
                    flex: 1,
                    child: _buildStatsPanel(systemState),
                  ),
                ],
              ),

              // Scenario Selector Overlay
              if (_showScenarios)
                Positioned(
                  top: 0,
                  bottom: 0,
                  left: 0,
                  right: 0,
                  child: GestureDetector(
                    onTap: () {
                      setState(() {
                        _showScenarios = false;
                      });
                    },
                    child: Container(
                      color: Colors.black87,
                      child: Center(
                        child: GestureDetector(
                          onTap: () {}, // Prevent closing when clicking inside
                          child: Container(
                            constraints: const BoxConstraints(
                              maxWidth: 600,
                              maxHeight: 700,
                            ),
                            child: Card(
                              elevation: 8,
                              child: Column(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(16),
                                    decoration: BoxDecoration(
                                      color: Colors.grey[850],
                                      borderRadius: const BorderRadius.only(
                                        topLeft: Radius.circular(12),
                                        topRight: Radius.circular(12),
                                      ),
                                    ),
                                    child: Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Row(
                                          children: [
                                            Icon(Icons.science, color: Colors.blue[400]),
                                            const SizedBox(width: 8),
                                            const Text(
                                              'Test Scenarios',
                                              style: TextStyle(
                                                fontSize: 20,
                                                fontWeight: FontWeight.bold,
                                                color: Colors.white,
                                              ),
                                            ),
                                          ],
                                        ),
                                        IconButton(
                                          icon: const Icon(Icons.close, color: Colors.white),
                                          onPressed: () {
                                            setState(() {
                                              _showScenarios = false;
                                            });
                                          },
                                        ),
                                      ],
                                    ),
                                  ),
                                  Expanded(
                                    child: SingleChildScrollView(
                                      padding: const EdgeInsets.all(16),
                                      child: ScenarioSelector(
                                        onScenarioSelected: () {
                                          setState(() {
                                            _showScenarios = false;
                                          });
                                        },
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          );
        },
      ),
      floatingActionButton: _buildFloatingActions(context),
    );
  }

  Widget _buildControlPanel(BuildContext context, Map<String, dynamic> state) {
    final processes = state['processes'] as List? ?? [];
    final resources = state['resources'] as List? ?? [];

    return Container(
      color: Colors.grey[900],
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Processes',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          if (processes.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(20),
                child: Text('No processes yet\nClick ⚗️ to load test scenarios'),
              ),
            )
          else
            ...processes.map((p) => ProcessCard(process: p)).toList(),
          const SizedBox(height: 20),
          const Text(
            'Resources',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          if (resources.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(20),
                child: Text('No resources yet'),
              ),
            )
          else
            ...resources.map((r) => ResourceCard(resource: r)).toList(),
        ],
      ),
    );
  }

  Widget _buildStatsPanel(Map<String, dynamic> state) {
    return Container(
      color: Colors.grey[850],
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          PredictionPanel(prediction: state['prediction'] ?? {}),
          const SizedBox(height: 20),
          _buildDeadlockStatus(state),
        ],
      ),
    );
  }

  Widget _buildDeadlockStatus(Map<String, dynamic> state) {
    final hasDeadlock = state['deadlock_detected'] ?? false;
    final deadlockedProcesses = state['deadlocked_processes'] as List? ?? [];

    return Card(
      color: hasDeadlock ? Colors.red[900] : Colors.green[900],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              hasDeadlock ? 'DEADLOCK DETECTED!' : 'System Running Normally',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            if (hasDeadlock) ...[
              const SizedBox(height: 10),
              const Text('Involved:'),
              ...deadlockedProcesses.map((p) => Text('  • $p')).toList(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildFloatingActions(BuildContext context) {
    final apiService = Provider.of<ApiService>(context, listen: false);

    return Column(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        FloatingActionButton(
          heroTag: 'add_process',
          onPressed: () => _showAddProcessDialog(context, apiService),
          child: const Icon(Icons.add),
          tooltip: 'Add Process',
        ),
        const SizedBox(height: 10),
        FloatingActionButton(
          heroTag: 'add_resource',
          onPressed: () => _showAddResourceDialog(context, apiService),
          child: const Icon(Icons.storage),
          tooltip: 'Add Resource',
        ),
      ],
    );
  }

  void _showAddProcessDialog(BuildContext context, ApiService apiService) {
    final nameController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create Process'),
        content: TextField(
          controller: nameController,
          decoration: const InputDecoration(labelText: 'Process Name'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              try {
                await apiService.createProcess(nameController.text, []);
                if (context.mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Process created')),
                  );
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: $e')),
                  );
                }
              }
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }

  void _showAddResourceDialog(BuildContext context, ApiService apiService) {
    final nameController = TextEditingController();
    final instancesController = TextEditingController(text: '1');

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create Resource'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(labelText: 'Resource Name'),
            ),
            TextField(
              controller: instancesController,
              decoration: const InputDecoration(labelText: 'Instances'),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              try {
                await apiService.createResource(
                  nameController.text,
                  int.parse(instancesController.text),
                );
                if (context.mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Resource created')),
                  );
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: $e')),
                  );
                }
              }
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }
}
