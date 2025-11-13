class ScenarioInfo {
  final String id;
  final String title;
  final String shortDescription;
  final String fullDescription;
  final String problemStatement;
  final List<String> keyPoints;
  final String category;
  final int processCount;
  final int resourceCount;

  const ScenarioInfo({
    required this.id,
    required this.title,
    required this.shortDescription,
    required this.fullDescription,
    required this.problemStatement,
    required this.keyPoints,
    required this.category,
    required this.processCount,
    required this.resourceCount,
  });

  static const Map<String, ScenarioInfo> scenarios = {
    'setup-deadlock': ScenarioInfo(
      id: 'setup-deadlock',
      title: 'Simple Deadlock (2 Processes)',
      shortDescription: 'Classic circular wait with P1 and P2',
      fullDescription: 'This demonstrates the most basic form of deadlock where two processes are waiting for each other\'s resources, creating a circular dependency that prevents both from proceeding.',
      problemStatement: '''Problem Statement:
Two processes P1 and P2 need two resources R1 and R2 to complete their tasks.

• Process P1 holds Resource R1 and requests Resource R2
• Process P2 holds Resource R2 and requests Resource R1
• Neither process can proceed, resulting in a deadlock

Real-World Example:
Think of two people crossing a narrow bridge from opposite sides. Each person holds one side of the bridge and needs the other side to cross, but neither will let go first.''',
      keyPoints: [
        'Demonstrates circular wait condition',
        'Both processes hold one resource and wait for another',
        'No process can make progress',
        'AI should predict 85-95% deadlock probability',
        'Common in database transaction scenarios'
      ],
      category: 'Basic',
      processCount: 2,
      resourceCount: 2,
    ),
    
    'setup-complex-deadlock': ScenarioInfo(
      id: 'setup-complex-deadlock',
      title: 'Complex Deadlock (3 Processes)',
      shortDescription: 'Three-way circular dependency',
      fullDescription: 'A more complex scenario involving three processes forming a circular chain of dependencies. This represents deadlocks in multi-threaded applications with multiple shared resources.',
      problemStatement: '''Problem Statement:
Three processes P1, P2, and P3 compete for three resources R1, R2, and R3.

• Process P1 holds R1, requests R2
• Process P2 holds R2, requests R3
• Process P3 holds R3, requests R1
• Creates a three-way circular wait

Real-World Example:
Three departments in a company each have one piece of equipment and need equipment from another department to complete their projects, forming a deadlock triangle.''',
      keyPoints: [
        'Multi-process circular dependency',
        'Harder to detect than 2-process deadlock',
        'Common in complex distributed systems',
        'AI prediction: 80-92% probability',
        'Requires sophisticated detection algorithms'
      ],
      category: 'Intermediate',
      processCount: 3,
      resourceCount: 3,
    ),
    
    'dining-philosophers': ScenarioInfo(
      id: 'dining-philosophers',
      title: 'Dining Philosophers Problem',
      shortDescription: '5 philosophers competing for 5 forks',
      fullDescription: 'The famous dining philosophers problem proposed by Edsger Dijkstra in 1965. Five philosophers sit at a round table with five forks, where each philosopher needs two forks to eat.',
      problemStatement: '''Problem Statement:
Five philosophers sit at a circular table with five forks placed between them.

• Each philosopher needs TWO forks (left and right) to eat
• Each philosopher currently holds their LEFT fork
• Each philosopher is waiting for their RIGHT fork (held by neighbor)
• All philosophers are stuck in a circular wait

Real-World Example:
Like a round-robin resource allocation where each entity holds one resource and needs the next one in sequence, common in networking protocols.''',
      keyPoints: [
        'Classic computer science problem from 1965',
        'Demonstrates resource starvation',
        '5-way circular dependency',
        'Used to teach synchronization concepts',
        'AI should predict very high deadlock probability (88-95%)'
      ],
      category: 'Classic',
      processCount: 5,
      resourceCount: 5,
    ),
    
    'reader-writer-deadlock': ScenarioInfo(
      id: 'reader-writer-deadlock',
      title: 'Reader-Writer Deadlock',
      shortDescription: 'Multiple readers/writers conflict',
      fullDescription: 'Demonstrates deadlock in reader-writer synchronization where multiple processes need both read and write access to shared resources in conflicting order.',
      problemStatement: '''Problem Statement:
Multiple readers and writers compete for ReadLock, WriteLock, and SharedData.

• Writer1 holds WriteLock, needs SharedData
• Reader1 holds SharedData, needs ReadLock
• Reader2 holds ReadLock, needs WriteLock
• Creates a three-way circular dependency

Real-World Example:
Database systems where transactions need both read and write locks on multiple tables, potentially causing deadlocks if not managed carefully.''',
      keyPoints: [
        'Common in database management systems',
        'Involves different lock types (read/write)',
        'Shows priority inversion problems',
        'Critical for concurrent data access',
        'Can cause system performance degradation'
      ],
      category: 'Database',
      processCount: 4,
      resourceCount: 3,
    ),
    
    'banker-unsafe-state': ScenarioInfo(
      id: 'banker-unsafe-state',
      title: "Banker's Algorithm - Unsafe State",
      shortDescription: 'Resource allocation unsafe state',
      fullDescription: 'Demonstrates Banker\'s Algorithm for deadlock avoidance. The system is in an unsafe state where no safe sequence of process execution exists.',
      problemStatement: '''Problem Statement:
System has 3 processes (P0, P1, P2) and 3 resource types (A, B, C).

• Available resources: [5, 4, 5]
• Current allocation leaves system in UNSAFE state
• No process can complete with available resources
• High probability of deadlock if new requests are granted

Real-World Example:
Memory management in operating systems where RAM allocation must ensure at least one process can complete to free up memory.''',
      keyPoints: [
        'Banker\'s Algorithm prevents deadlock',
        'Calculates safe sequences before allocation',
        'Used in OS resource management',
        'Conservative approach - may reject valid requests',
        'Trade-off between safety and efficiency'
      ],
      category: 'Algorithm',
      processCount: 3,
      resourceCount: 3,
    ),
    
    'hold-and-wait': ScenarioInfo(
      id: 'hold-and-wait',
      title: 'Hold and Wait Condition',
      shortDescription: '4 processes in circular chain',
      fullDescription: 'Demonstrates the "Hold and Wait" condition - one of four necessary conditions for deadlock. Processes hold resources while waiting for additional resources.',
      problemStatement: '''Problem Statement:
Four processes need multiple I/O devices:

• Process_A holds Printer, waits for Scanner
• Process_B holds Scanner, waits for HardDisk
• Process_C holds HardDisk, waits for Memory
• Process_D holds Memory, waits for Printer
• Forms a complete circular chain

Real-World Example:
Print job management where documents need multiple output devices (printer, scanner, fax) in sequence.''',
      keyPoints: [
        'One of four necessary conditions for deadlock',
        'Processes hold AND wait simultaneously',
        'Prevention: request all resources at once',
        'Common in I/O device management',
        'Wait times increase system inefficiency'
      ],
      category: 'Conditions',
      processCount: 4,
      resourceCount: 4,
    ),
    
    'no-preemption-deadlock': ScenarioInfo(
      id: 'no-preemption-deadlock',
      title: 'No Preemption Deadlock',
      shortDescription: 'Database transaction deadlock',
      fullDescription: 'Resources cannot be forcefully taken away (preempted). Once allocated, they must be voluntarily released. Common in database transaction management.',
      problemStatement: '''Problem Statement:
Two database transactions hold critical locks:

• Transaction 1 has TableLock_Users, needs IndexLock_Orders
• Transaction 2 has IndexLock_Orders, needs TableLock_Users
• Database locks CANNOT be preempted (ACID properties)
• Transactions are blocked waiting for each other

Real-World Example:
Banking transactions where account locks cannot be interrupted mid-transaction to maintain data consistency and ACID properties.''',
      keyPoints: [
        'Resources cannot be forcibly taken',
        'Critical for transaction integrity (ACID)',
        'Common in database systems',
        'High wait times (140-150ms)',
        'Automatic deadlock detection needed'
      ],
      category: 'Database',
      processCount: 2,
      resourceCount: 2,
    ),
    
    'large-scale-deadlock': ScenarioInfo(
      id: 'large-scale-deadlock',
      title: 'Large Scale Deadlock',
      shortDescription: 'Complex system with 10 workers',
      fullDescription: 'Tests system scalability with 10 processes and 8 resources. Represents real-world distributed systems with many concurrent tasks.',
      problemStatement: '''Problem Statement:
Large distributed system with 10 worker processes and 8 shared resources.

• Multiple circular dependencies across the system
• Complex resource allocation patterns
• Difficult to detect and visualize
• Tests AI model's ability to handle scale

Real-World Example:
Cloud computing environments with multiple microservices competing for shared resources like databases, caches, and message queues.''',
      keyPoints: [
        'Tests detection algorithm scalability',
        '10 processes, 8 resources',
        'Complex circular dependencies',
        'Represents real distributed systems',
        'AI must detect patterns in complex graphs'
      ],
      category: 'Advanced',
      processCount: 10,
      resourceCount: 8,
    ),
    
    'near-deadlock-high-risk': ScenarioInfo(
      id: 'near-deadlock-high-risk',
      title: 'Near Deadlock - High Risk',
      shortDescription: 'System on edge of deadlock',
      fullDescription: 'System is very close to deadlock but hasn\'t reached it yet. Tests the AI\'s predictive capability to detect deadlocks before they occur.',
      problemStatement: '''Problem Statement:
Three critical processes with very limited resources:

• 100% resource utilization
• High wait times (110-120ms)
• All processes in "waiting" state
• One more resource request will trigger deadlock

Real-World Example:
Production servers running at maximum capacity where one more request could trigger a cascade failure and system-wide deadlock.''',
      keyPoints: [
        'Tests AI prediction capability',
        'No actual deadlock YET',
        '100% resource utilization',
        'Very high wait times',
        'AI should predict 75-85% probability'
      ],
      category: 'Predictive',
      processCount: 3,
      resourceCount: 3,
    ),
    
    'setup-safe-state': ScenarioInfo(
      id: 'setup-safe-state',
      title: 'Safe State (No Deadlock)',
      shortDescription: 'System running safely',
      fullDescription: 'Control scenario showing a system in a safe state with no deadlock. Resources are available and processes can complete.',
      problemStatement: '''Problem Statement:
Two processes with multiple resource instances:

• Resource_A has 3 instances (sufficient for both)
• Resource_B has 2 instances
• P1 holds 1 instance of R1
• P2 holds 1 instance of R2
• NO circular wait, plenty of resources available

Real-World Example:
Well-designed systems with proper resource provisioning and load balancing that avoid deadlock conditions.''',
      keyPoints: [
        'Demonstrates safe system state',
        'No circular dependencies',
        'Adequate resources available',
        'AI should predict LOW risk (<30%)',
        'Baseline for comparison with deadlock states'
      ],
      category: 'Control',
      processCount: 2,
      resourceCount: 2,
    ),
  };
}
