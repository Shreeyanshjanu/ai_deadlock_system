import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

class WebSocketService extends ChangeNotifier {
  WebSocketChannel? _channel;
  Map<String, dynamic>? _systemState;
  bool _isConnected = false;
  
  Map<String, dynamic>? get systemState => _systemState;
  bool get isConnected => _isConnected;
  
  void connect() {
    try {
      _channel = WebSocketChannel.connect(
        Uri.parse('ws://localhost:8000/ws'),
      );
      
      _isConnected = true;
      notifyListeners();
      
      _channel!.stream.listen(
        (data) {
          _systemState = jsonDecode(data);
          notifyListeners();
        },
        onError: (error) {
          _isConnected = false;
          notifyListeners();
        },
        onDone: () {
          _isConnected = false;
          notifyListeners();
        },
      );
    } catch (e) {
      _isConnected = false;
      notifyListeners();
    }
  }
  
  void disconnect() {
    _channel?.sink.close();
    _isConnected = false;
    notifyListeners();
  }
  
  @override
  void dispose() {
    disconnect();
    super.dispose();
  }
}
