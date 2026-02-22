# Graph RAG

## What

### RAG

RAG（Retrieval-Augmented Generation）是一种结合检索和生成技术的大规模语言模型应用方法。它旨在提升生成模型的准确性，特别是在需要记忆大量事实性信息或特定领域知识的场景中。RAG通常由两个主要部分组成：一个大语言模型（如Transformer模型）和一个知识检索系统（通常是文档库或知识库）。具体工作流程如下：

### 概念

1. **检索模块**：首先，它通过查询（通常是用户的问题或对话的一部分）在预先构建的大型文本或知识库中快速检索出最相关的几个文档或片段。
2. **融合模块**：检索到的信息随后被以某种形式（例如，直接嵌入、摘要或指针）融入到语言模型的输入序列中，或者直接用于影响模型的注意力机制。
3. **生成模块**：增强后的语言模型利用这些上下文信息来生成回答或完成任务，这使得生成的答案不仅基于模式学习，还基于具体查询相关的精确信息。

### 方法

- **直接融合方法**：在模型输入序列中直接添加检索到的文本摘要或关键句。
- **注意力引导**：使用检索信息引导模型的注意力机制，确保在生成答案时考虑这些信息。
- **指针网络**：模型内部使用指针来直接引用检索到的文本片段，这可减少重复生成数据的可能性，确保答案的准确性和新颖性。

### 实例

假设我们构建一个能够回答历史问题的RAG模型。步骤如下：

1. **数据准备**：构建一个大型历史文献数据库，包含重要的历史事件、日期和人物资料。
2. **检索模块**：用户提问，比如“美国独立宣言是在哪一年签署的？”系统通过关键词检索在文献库中快速找到包含“美国独立宣言”和“签署年份”的文档片段。
3. **融合与生成**：检索到的信息（例如，“1776年7月4日”）被作为上下文提供给大语言模型，模型利用这个信息生成回答：“美国独立宣言是在1776年签署的。”
4. **输出**：系统返回准确回答，提高了从纯生成模型可能无法确切知道具体年份的情况下的回答准确性。

RAG的应用不仅仅局限于问答系统，它还可以应用于对话系统、个性化推荐、新闻摘要生成等众多需要结合广泛知识和上下文理解的场景。通过有效地结合大规模语言模型和精确信息检索，RAG显著增强了AI系统对复杂和依赖于具体信息问题的处理能力

### Graph RAG

Graph RAG 是一种基于知识图谱的检索增强技术，通过构建图模型的知识表达，将实体和关系之间的联系用图的形式进行展示，然后利用大语言模型 LLM（Large Language Model）进行检索增强。

图数据库凭借图形格式组织和连接信息的方式，天然适合存储及表达复杂的上下文信息。通过图技术构建知识图谱提升 In-Context  Learning 的全面性为用户提供更多的上下文信息，能够帮助大语言模型（LLM）更好地理解实体间的关系，提升自己的表达和推理能力。

Graph RAG 将知识图谱等价于一个超大规模的词汇表，而实体和关系则对应于单词。通过这种方式，Graph RAG 在检索时能够将实体和关系作为单元进行联合建模，从而更准确地理解查询意图，并提供更精准的检索结果。

## How

通过知识图谱（Knowledge Graph, KG）对大语言模型（LLM）返回的结果进行检索增强生成（Retrieval-Augmented Generation, RAG）可以提高生成内容的准确性和一致性。以下是一个概述如何实现这一目标的步骤：

### 1. **构建或使用现有的知识图谱**
   - **数据来源**: 知识图谱通常由结构化数据（如关系数据库）、半结构化数据（如JSON、XML）、以及非结构化数据（如文档、网页）构建而成。
   - **存储和查询**: 可以使用Neo4j、Memgraph等图数据库来存储知识图谱，并通过Cypher或其他查询语言进行查询。

### 2. **结合知识图谱进行查询增强**
   - **查询扩展**: 在用户发出查询后，使用知识图谱对查询进行扩展。例如，如果用户询问某一特定领域的问题，可以使用知识图谱扩展相关领域的概念和关系。
   - **上下文检索**: 在生成答案之前，使用知识图谱对相关上下文信息进行检索，这些信息可以包括实体之间的关系、属性、历史记录等。

### 3. **与大语言模型结合**
   - **预处理**: 在将用户的查询输入大语言模型之前，先用知识图谱检索相关的上下文信息，并将这些信息附加到查询中，以增强模型的理解。
   - **生成与验证**: 大语言模型生成初步答案后，可以通过知识图谱对生成的内容进行验证和修正。例如，验证生成的实体关系是否正确，或对关键事实进行交叉验证。
   - **后处理**: 使用知识图谱进行后处理，以确保生成的结果与知识图谱中的已知事实一致。

### 4. **实现流程**
   - **用户查询**: 接收到用户查询后，系统首先通过知识图谱检索相关实体和关系。
   - **检索增强**: 将检索到的信息与用户查询一起传递给大语言模型，增强生成过程。
   - **结果验证**: 对生成的结果进行验证，确保其与知识图谱中的信息一致。
   - **结果返回**: 将经过验证的答案返回给用户。

### 5. **技术实现**
   - **Python与图数据库**: 使用Python脚本连接图数据库（如Neo4j），通过Cypher查询获取知识图谱中的信息。
   - **与大语言模型集成**: 使用Python库（如OpenAI的API）与大语言模型交互，将检索到的上下文信息传递给模型，并获取生成的答案。

### 6. **示例代码**
   下面是一个简单的Python示例，展示了如何结合Neo4j的知识图谱与OpenAI的大语言模型进行RAG：

   ```python
   from neo4j import GraphDatabase
   import openai

   # 连接到Neo4j数据库
   uri = "bolt://localhost:7687"
   driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

   def retrieve_kg_context(query):
       with driver.session() as session:
           result = session.run(query)
           context = [record["context"] for record in result]
           return " ".join(context)

   def generate_response_with_context(prompt, context):
       combined_prompt = f"{context}\n\n{prompt}"
       response = openai.Completion.create(
           engine="text-davinci-003",
           prompt=combined_prompt,
           max_tokens=150
       )
       return response.choices[0].text.strip()

   # 示例查询
   kg_query = "MATCH (n:Entity)-[r:RELATION]->(m) WHERE n.name='example' RETURN m.name AS context"
   context = retrieve_kg_context(kg_query)

   # 用户输入
   user_query = "Explain the relationship between example and its connected entities."

   # 生成结果
   response = generate_response_with_context(user_query, context)
   print(response)
   ```

通过上述方法，知识图谱可以显著增强大语言模型的生成能力，使其输出更加精确和有意义。

# Reference
* https://developer.aliyun.com/article/1318513