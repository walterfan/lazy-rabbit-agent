# Graph RAG

## What

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