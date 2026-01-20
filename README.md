# Pre-Processing-Agent

In this project, police data is cleaned so that it works better for AI inputs. To do this, a pipeline is set up that performs three tasks that are done by three agents/LLMs: 
1. **Data Cleaning Expert Agent**:
  Collect the characteristics of the data and find out how it can be cleaned.
2. **Data Cleaning Agent**:
  Implement the code to execute the proposed steps.
3. **Code Execution Agent**:
  Then execute the code to obtain the cleaned data.
For each of the three steps, an LLM is used to perform the task. The LLM used is LLM3 by OpenAI
