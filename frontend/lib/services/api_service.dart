import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://localhost:8000';
  
  Future<Map<String, dynamic>> createProcess(String name, List<int> resources) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/process/create'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'name': name, 'resources': resources}),
    );
    
    return jsonDecode(response.body);
  }
  
  Future<Map<String, dynamic>> createResource(String name, int instances) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/resource/create'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'name': name, 'instances': instances}),
    );
    
    return jsonDecode(response.body);
  }
  
  Future<Map<String, dynamic>> requestResource(int processId, int resourceId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/process/request'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'process_id': processId, 'resource_id': resourceId}),
    );
    
    return jsonDecode(response.body);
  }
  
  Future<Map<String, dynamic>> releaseResource(int processId, int resourceId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/process/release'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'process_id': processId, 'resource_id': resourceId}),
    );
    
    return jsonDecode(response.body);
  }
  
  Future<Map<String, dynamic>> getSystemState() async {
    final response = await http.get(Uri.parse('$baseUrl/api/system/state'));
    return jsonDecode(response.body);
  }
  
  Future<void> resetSystem() async {
    await http.post(Uri.parse('$baseUrl/api/system/reset'));
  }
}
