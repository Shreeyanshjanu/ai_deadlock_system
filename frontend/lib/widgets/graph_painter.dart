import 'package:flutter/material.dart';
import 'dart:math' as math;

class GraphVisualization extends StatelessWidget {
  final Map<String, dynamic> graphData;
  
  const GraphVisualization({Key? key, required this.graphData}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.grey[800],
      child: CustomPaint(
        painter: GraphPainter(graphData),
        child: Container(),
      ),
    );
  }
}

class GraphPainter extends CustomPainter {
  final Map<String, dynamic> graphData;
  
  GraphPainter(this.graphData);

  @override
  void paint(Canvas canvas, Size size) {
    final nodes = graphData['nodes'] as List? ?? [];
    final edges = graphData['edges'] as List? ?? [];
    
    if (nodes.isEmpty) {
      _drawEmptyState(canvas, size);
      return;
    }
    
    // Calculate node positions in circular layout
    final positions = _calculatePositions(nodes, size);
    
    // Draw edges
    for (var edge in edges) {
      _drawEdge(canvas, positions[edge['source']], positions[edge['target']]);
    }
    
    // Draw nodes
    for (var node in nodes) {
      final pos = positions[node['id']];
      final isProcess = node['type'] == 'process';
      _drawNode(canvas, pos!, node['id'], isProcess);
    }
  }
  
  Map<String, Offset> _calculatePositions(List nodes, Size size) {
    final positions = <String, Offset>{};
    final centerX = size.width / 2;
    final centerY = size.height / 2;
    final radius = math.min(centerX, centerY) * 0.7;
    
    for (var i = 0; i < nodes.length; i++) {
      final angle = (2 * math.pi * i) / nodes.length;
      final x = centerX + radius * math.cos(angle);
      final y = centerY + radius * math.sin(angle);
      positions[nodes[i]['id']] = Offset(x, y);
    }
    
    return positions;
  }
  
  void _drawEdge(Canvas canvas, Offset? start, Offset? end) {
    if (start == null || end == null) return;
    
    final paint = Paint()
      ..color = Colors.blue.withOpacity(0.6)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;
    
    canvas.drawLine(start, end, paint);
    
    // Draw arrow
    _drawArrow(canvas, start, end, paint);
  }
  
  void _drawArrow(Canvas canvas, Offset start, Offset end, Paint paint) {
    const arrowSize = 10.0;
    final direction = (end - start);
    final angle = math.atan2(direction.dy, direction.dx);
    
    final arrowPoint1 = Offset(
      end.dx - arrowSize * math.cos(angle - math.pi / 6),
      end.dy - arrowSize * math.sin(angle - math.pi / 6),
    );
    
    final arrowPoint2 = Offset(
      end.dx - arrowSize * math.cos(angle + math.pi / 6),
      end.dy - arrowSize * math.sin(angle + math.pi / 6),
    );
    
    final path = Path()
      ..moveTo(end.dx, end.dy)
      ..lineTo(arrowPoint1.dx, arrowPoint1.dy)
      ..moveTo(end.dx, end.dy)
      ..lineTo(arrowPoint2.dx, arrowPoint2.dy);
    
    canvas.drawPath(path, paint);
  }
  
  void _drawNode(Canvas canvas, Offset position, String label, bool isProcess) {
    final paint = Paint()
      ..color = isProcess ? Colors.green : Colors.orange
      ..style = PaintingStyle.fill;
    
    if (isProcess) {
      canvas.drawCircle(position, 30, paint);
    } else {
      canvas.drawRect(
        Rect.fromCenter(center: position, width: 50, height: 50),
        paint,
      );
    }
    
    // Draw label
    final textPainter = TextPainter(
      text: TextSpan(
        text: label,
        style: const TextStyle(color: Colors.white, fontSize: 12),
      ),
      textDirection: TextDirection.ltr,
    );
    
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(position.dx - textPainter.width / 2, position.dy - textPainter.height / 2),
    );
  }
  
  void _drawEmptyState(Canvas canvas, Size size) {
    final textPainter = TextPainter(
      text: const TextSpan(
        text: 'No processes or resources yet',
        style: TextStyle(color: Colors.white54, fontSize: 18),
      ),
      textDirection: TextDirection.ltr,
    );
    
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        (size.width - textPainter.width) / 2,
        (size.height - textPainter.height) / 2,
      ),
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
