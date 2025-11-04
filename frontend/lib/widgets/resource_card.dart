import 'package:flutter/material.dart';

class ResourceCard extends StatelessWidget {
  final Map<String, dynamic> resource;
  
  const ResourceCard({Key? key, required this.resource}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final available = resource['available'] ?? 0;
    final total = resource['instances'] ?? 1;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: const CircleAvatar(
          backgroundColor: Colors.orange,
          child: Icon(Icons.storage, color: Colors.white),
        ),
        title: Text(resource['name'] ?? 'Resource ${resource['id']}'),
        subtitle: Text('Available: $available / $total'),
        trailing: Text('ID: ${resource['id']}'),
      ),
    );
  }
}
