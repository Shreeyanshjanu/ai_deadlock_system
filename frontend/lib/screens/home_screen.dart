import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/websocket_service.dart';
import '../services/api_service.dart';
import '../widgets/process_card.dart';
import '../widgets/resource_card.dart';
import '../widgets/prediction_panel.dart';
import '../widgets/graph_painter.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<WebSocketService>(context, listen: false).connect();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Deadlock Detection System'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () async {
              await Provider.of<ApiService>(context, listen: false).resetSystem();
            },
          ),
        ],
      ),
      body: Consumer<WebSocketService>(
        builder: (context, wsService, child) {
          if (!wsService.isConnected) {
            return const Center(child: CircularProgressIndicator());
          }
          
          final systemState = wsService.systemState;
          if (systemState == null) {
            return const Center(child: Text('Waiting for data...'));
          }
          
          return Row(
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
          ...processes.map((p) => ProcessCard(process: p)).toList(),
          const SizedBox(height: 20),
          const Text(
            'Resources',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
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
              await apiService.createProcess(nameController.text, []);
              Navigator.pop(context);
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
              await apiService.createResource(
                nameController.text,
                int.parse(instancesController.text),
              );
              Navigator.pop(context);
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }
}
