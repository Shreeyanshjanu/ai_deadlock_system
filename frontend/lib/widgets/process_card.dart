import 'package:flutter/material.dart';

class ProcessCard extends StatelessWidget {
  final Map<String, dynamic> process;
  
  const ProcessCard({Key? key, required this.process}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: const CircleAvatar(
          backgroundColor: Colors.green,
          child: Icon(Icons.computer, color: Colors.white),
        ),
        title: Text(process['name'] ?? 'Process ${process['id']}'),
        subtitle: Text('State: ${process['state'] ?? 'unknown'}'),
        trailing: Text('ID: ${process['id']}'),
      ),
    );
  }
}
