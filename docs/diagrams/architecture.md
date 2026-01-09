# MageAgent Architecture Diagrams

## System Overview

```mermaid
graph TB
    subgraph "User Interface"
        MB[Menu Bar App<br/>MageAgentMenuBar.app]
        CLI[Claude Code CLI]
        API[Direct API Calls]
    end

    subgraph "MageAgent Server :3457"
        FW[FastAPI Server]
        OR[Orchestrator]
        TE[Tool Executor]

        subgraph "Patterns"
            AUTO[auto - Task Router]
            EXEC[execute - ReAct Loop]
            HYB[hybrid - Reasoning + Tools]
            VAL[validated - Gen + Validate]
            COMP[compete - Multi-model Judge]
        end
    end

    subgraph "MLX Models"
        M72[Qwen-72B Q8<br/>77GB - Reasoning]
        M8[Hermes-3 8B Q8<br/>9GB - Tool Calling]
        M7[Qwen-Coder 7B<br/>5GB - Validation]
        M32[Qwen-Coder 32B<br/>18GB - Coding]
    end

    subgraph "External"
        FS[File System]
        WEB[Web Search]
        BASH[Bash Commands]
    end

    MB --> FW
    CLI --> FW
    API --> FW

    FW --> OR
    OR --> AUTO
    OR --> EXEC
    OR --> HYB
    OR --> VAL
    OR --> COMP

    AUTO --> M7
    EXEC --> M72
    EXEC --> M8
    HYB --> M72
    HYB --> M8
    VAL --> M72
    VAL --> M7
    COMP --> M72
    COMP --> M32
    COMP --> M7

    TE --> FS
    TE --> WEB
    TE --> BASH

    EXEC --> TE
```

## Menu Bar App Architecture (v2.1)

```mermaid
graph TB
    subgraph "MageAgentMenuBar.app"
        AD[AppDelegate]
        SI[NSStatusItem]
        MN[NSMenu]

        subgraph "Menu Items"
            ST[Status Display]
            SP[System Pressure<br/>● Memory / CPU / GPU]
            SC[Server Control<br/>Start/Stop/Restart]
            WM[Warmup Models]
            LM[Load Models Submenu]
            PT[Patterns Submenu]
            UT[Utilities<br/>Docs/Logs/Test/Settings]
        end

        subgraph "System Monitoring"
            MT[Memory Monitor<br/>vm_statistics64]
            CT[CPU Monitor<br/>host_processor_info]
            GT[GPU/Metal Monitor<br/>Unified Memory]
        end

        subgraph "Windows"
            TW[Test Results Window]
            SW[Settings Alert]
            TT[Toast Notifications]
        end
    end

    subgraph "External"
        SRV[MageAgent Server<br/>localhost:3457]
        SCR[mageagent-server.sh]
        LOG[Log Files]
    end

    AD --> SI
    SI --> MN
    MN --> ST
    MN --> SP
    MN --> SC
    MN --> WM
    MN --> LM
    MN --> PT
    MN --> UT

    AD --> MT
    AD --> CT
    AD --> GT
    MT --> SP
    CT --> SP
    GT --> SP

    AD --> TW
    AD --> SW
    AD --> TT

    SC --> SCR
    AD --> SRV
    UT --> LOG
```

## Timeout Architecture (v2.1)

```mermaid
flowchart TD
    subgraph "Request Flow with Timeout"
        REQ[API Request] --> GEN[generate_with_model]
        GEN --> LOCK{Acquire<br/>asyncio.Lock}
        LOCK --> LOAD[load_model_async]
        LOAD --> WAIT[asyncio.wait_for<br/>with timeout]

        WAIT --> |Success| RESP[Return Response]
        WAIT --> |Timeout| ERR[GenerationTimeoutError]

        ERR --> HTTP504[HTTP 504<br/>Gateway Timeout]
        RESP --> HTTP200[HTTP 200<br/>Success]
    end

    subgraph "Timeout Configuration"
        CFG[TIMEOUT_CONFIG]
        CFG --> |validator| T60[60 seconds]
        CFG --> |tools| T120[120 seconds]
        CFG --> |competitor| T180[180 seconds]
        CFG --> |primary| T600[600 seconds]
    end

    GEN --> CFG
```

## System Pressure Monitoring

```mermaid
graph TB
    subgraph "System Pressure Indicators"
        direction LR
        GREEN[● Green<br/>Normal<br/>Memory < 75%<br/>CPU < 70%]
        YELLOW[● Yellow<br/>Warning<br/>Memory 75-90%<br/>CPU 70-90%]
        RED[● Red<br/>Critical<br/>Memory > 90%<br/>CPU > 90%]
    end

    subgraph "Data Sources"
        MEM[vm_statistics64<br/>active + wired + compressed]
        CPU[host_processor_info<br/>user + system + nice ticks]
        GPU[Loaded Models<br/>Unified Memory Usage]
    end

    MEM --> |used/total GB| GREEN
    CPU --> |usage %| GREEN
    GPU --> |model count| GREEN
```

## Pattern Flow Diagrams

### Execute Pattern (ReAct Loop)

```mermaid
sequenceDiagram
    participant U as User
    participant S as Server
    participant Q as Qwen-72B
    participant H as Hermes-3
    participant T as Tool Executor

    U->>S: Request with tools needed
    S->>Q: Generate response
    Q->>S: Response with tool intentions
    S->>H: Extract tool calls
    H->>S: Structured tool calls JSON
    S->>T: Execute tools
    T->>S: Tool results
    S->>Q: Continue with results
    Q->>S: Final response
    S->>U: Complete answer
```

### Validated Pattern

```mermaid
sequenceDiagram
    participant U as User
    participant S as Server
    participant Q as Qwen-72B (Generator)
    participant V as Qwen-7B (Validator)

    U->>S: Request
    S->>Q: Generate code/response
    Q->>S: Initial response
    S->>V: Validate response
    V->>S: Validation result + issues
    alt Has Issues
        S->>Q: Revise with feedback
        Q->>S: Revised response
    end
    S->>U: Final validated response
```

### Compete Pattern

```mermaid
sequenceDiagram
    participant U as User
    participant S as Server
    participant Q72 as Qwen-72B
    participant Q32 as Qwen-32B
    participant J as Qwen-7B (Judge)

    U->>S: Request
    par Generate in Parallel
        S->>Q72: Generate response
        S->>Q32: Generate response
    end
    Q72->>S: Response A
    Q32->>S: Response B
    S->>J: Judge responses
    J->>S: Best response selection
    S->>U: Winning response
```

## Model Memory Layout

```mermaid
pie title GPU/Unified Memory Usage (M4 Max 128GB)
    "Qwen-72B Q8" : 77
    "Qwen-Coder 32B" : 18
    "Hermes-3 8B Q8" : 9
    "Qwen-Coder 7B" : 5
    "Available" : 19
```

## Installation Flow

```mermaid
flowchart TD
    A[Clone Repository] --> B[Run npm install]
    B --> C[Install Python Dependencies]
    C --> D{Download MLX Models?}
    D -->|Yes| E[Download Models<br/>~109GB total]
    D -->|Skip| F[Use on-demand loading]
    E --> G[Build Menu Bar App]
    F --> G
    G --> H[Install to /Applications]
    H --> I[Configure LaunchAgent]
    I --> J[Start Server]
    J --> K[Verify Installation]
    K --> L[Ready to Use!]
```

## API Endpoints

```mermaid
graph LR
    subgraph "OpenAI-Compatible API"
        H[/health]
        M[/v1/models]
        C[/v1/chat/completions]
    end

    subgraph "Response Format"
        H --> |JSON| HS[status, loaded_models]
        M --> |JSON| MS[model list]
        C --> |JSON/SSE| CS[chat completion]
    end
```
