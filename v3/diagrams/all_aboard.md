# All Aboard - System Architecture

## Overview
The system implements a publish-subscribe (pub/sub) messaging pattern using ZeroMQ, allowing for decoupled communication between services.

## Core Components

### 1. Messaging System
- **Message Proxy**: Central hub that manages message routing
- **Message Class**: Standardized message format with topics and payloads

### 2. Service Architecture
```
[ServiceA] ←→ [Message Proxy] ←→ [ServiceB]
    ↑          (PUB/SUB)           ↑
    └─────── Base Service Class ───┘
```

### 3. Message Flow
1. Services connect to proxy endpoints
2. Publishers send messages to specific topics
3. Subscribers receive messages for their subscribed topics
4. Messages are processed asynchronously

### 4. Implementation Details
- Async/await pattern for non-blocking operations
- UUID-based service identification
- Standardized logging across components
- Topic-based message filtering
- Error handling and recovery

## Topics
- topic1: Messages handled by ServiceA
- topic2: Messages handled by ServiceB

## Example Flow
```
ServiceA → [topic2] → Proxy → ServiceB
ServiceB → [topic1] → Proxy → ServiceA
```

## Benefits
1. Loose coupling between services
2. Scalable architecture
3. Async message processing
4. Reliable message delivery
5. Easy service extension
