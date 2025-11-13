import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/scenario_info_panel.dart';

class ScenarioSelector extends StatelessWidget {
  final VoidCallback? onScenarioSelected;

  const ScenarioSelector({Key? key, this.onScenarioSelected}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final apiService = ApiService();
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[850],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
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
          const SizedBox(height: 16),
          _buildScenarioButton(
            context,
            'Simple Deadlock (2 Processes)',
            'Classic circular wait with P1 and P2',
            Icons.link,
            Colors.orange,
            () => apiService.runTestScenario('setup-deadlock'),
            'setup-deadlock',
          ),
          const SizedBox(height: 8),
          _buildScenarioButton(
            context,
            'Complex Deadlock (3 Processes)',
            'Three-way circular dependency',
            Icons.device_hub,
            Colors.red,
            () => apiService.runTestScenario('setup-complex-deadlock'),
            'setup-complex-deadlock',
          ),
          const SizedBox(height: 8),
          _buildScenarioButton(
            context,
            'Dining Philosophers',
            '5 philosophers competing for 5 forks',
            Icons.restaurant,
            Colors.purple,
            () => apiService.runTestScenario('dining-philosophers'),
            'dining-philosophers',
          ),
          const SizedBox(height: 8),
          _buildScenarioButton(
            context,
            'Reader-Writer Deadlock',
            'Multiple readers/writers conflict',
            Icons.book,
            Colors.teal,
            () => apiService.runTestScenario('reader-writer-deadlock'),
            'reader-writer-deadlock',
          ),
          const SizedBox(height: 8),
          _buildScenarioButton(
            context,
            "Banker's Unsafe State",
            'Resource allocation unsafe state',
            Icons.account_balance,
            Colors.amber,
            () => apiService.runTestScenario('banker-unsafe-state'),
            'banker-unsafe-state',
          ),
          const SizedBox(height: 8),
          _buildScenarioButton(
            context,
            'Hold and Wait',
            '4 processes in circular chain',
            Icons.lock_clock,
            Colors.deepOrange,
            () => apiService.runTestScenario('hold-and-wait'),
            'hold-and-wait',
          ),
          const SizedBox(height: 8),
          _buildScenarioButton(
            context,
            'No Preemption',
            'Database transaction deadlock',
            Icons.storage,
            Colors.indigo,
            () => apiService.runTestScenario('no-preemption-deadlock'),
            'no-preemption-deadlock',
          ),
          const SizedBox(height: 8),
          _buildScenarioButton(
            context,
            'Large Scale (10 Processes)',
            'Complex system with 10 workers',
            Icons.grid_view,
            Colors.pink,
            () => apiService.runTestScenario('large-scale-deadlock'),
            'large-scale-deadlock',
          ),
          const SizedBox(height: 8),
          _buildScenarioButton(
            context,
            'Near Deadlock (High Risk)',
            'System on edge of deadlock',
            Icons.warning,
            Colors.yellow[700]!,
            () => apiService.runTestScenario('near-deadlock-high-risk'),
            'near-deadlock-high-risk',
          ),
          const SizedBox(height: 8),
          _buildScenarioButton(
            context,
            'Safe State (No Deadlock)',
            'System running safely',
            Icons.check_circle,
            Colors.green,
            () => apiService.runTestScenario('setup-safe-state'),
            'setup-safe-state',
          ),
        ],
      ),
    );
  }

  Widget _buildScenarioButton(
    BuildContext context,
    String title,
    String description,
    IconData icon,
    Color color,
    Future<void> Function() onPressed,
    String scenarioId,
  ) {
    return InkWell(
      onTap: () async {
        try {
          await onPressed();
          if (context.mounted) {
            if (onScenarioSelected != null) {
              onScenarioSelected!();
            }
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('$title loaded successfully!'),
                backgroundColor: Colors.green,
                duration: const Duration(seconds: 2),
              ),
            );
          }
        } catch (e) {
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Error: $e'),
                backgroundColor: Colors.red,
                duration: const Duration(seconds: 3),
              ),
            );
          }
        }
      },
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.grey[800],
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.5)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: color, size: 24),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    description,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[400],
                    ),
                  ),
                ],
              ),
            ),
            // Info button
            IconButton(
              icon: const Icon(Icons.info_outline, size: 20),
              color: Colors.blue[400],
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (context) => ScenarioInfoPanel(scenarioId: scenarioId),
                );
              },
              tooltip: 'View Details',
            ),
            const SizedBox(width: 4),
            Icon(Icons.play_arrow, color: color, size: 20),
          ],
        ),
      ),
    );
  }
}
