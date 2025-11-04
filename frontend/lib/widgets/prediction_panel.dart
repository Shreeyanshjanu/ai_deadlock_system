import 'package:flutter/material.dart';

class PredictionPanel extends StatelessWidget {
  final Map<String, dynamic> prediction;
  
  const PredictionPanel({Key? key, required this.prediction}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final probability = prediction['deadlock_probability'] ?? 0.0;
    final riskLevel = prediction['risk_level'] ?? 'LOW';
    
    Color getRiskColor() {
      switch (riskLevel) {
        case 'HIGH':
          return Colors.red;
        case 'MEDIUM':
          return Colors.orange;
        default:
          return Colors.green;
      }
    }
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'AI Prediction',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Text(
              'Risk Level: $riskLevel',
              style: TextStyle(
                fontSize: 16,
                color: getRiskColor(),
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            LinearProgressIndicator(
              value: probability,
              backgroundColor: Colors.grey[700],
              valueColor: AlwaysStoppedAnimation<Color>(getRiskColor()),
            ),
            const SizedBox(height: 5),
            Text('Probability: ${(probability * 100).toStringAsFixed(1)}%'),
          ],
        ),
      ),
    );
  }
}
