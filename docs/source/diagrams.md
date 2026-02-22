# Diagram support (Mermaid and PlantUML)

The docs use **Mermaid** (built-in, no extra install) and **PlantUML** (optional, requires `plantuml` in PATH or Java + plantuml.jar).

## Mermaid

Use the `{mermaid}` directive in any `.md` file:

```{mermaid}
flowchart LR
  A[Start] --> B{OK?}
  B -->|Yes| C[End]
  B -->|No| A
```

Supported: flowcharts, sequence diagrams, state, class, ER, and more. See [Mermaid docs](https://mermaid.js.org/).

## PlantUML

Requires `plantuml` executable or `conf.py` setting:

```python
plantuml = 'java -jar /path/to/plantuml.jar'
```

Example in a `.md` file:

```{uml}
@startuml
actor User
participant "Backend" as BE
User -> BE: Request
BE --> User: Response
@enduml
```

Output format is SVG (config: `plantuml_output_format = 'svg_img'`). Cache: `_plantuml_cache/`.
