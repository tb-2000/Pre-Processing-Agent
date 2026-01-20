# Pre-Processing-Agent

In this project, police data is cleaned so that it works better for AI inputs. To do this, a pipeline is set up that performs three tasks that are done by three agents/LLMs: 
1.) Collect the characteristics of the data and find out how it can be cleaned. (Data Cleaning Expert Agent)
2.) Implement the code to execute the proposed steps. (Data Cleaning Agent)
3.) Then execute the code to obtain the cleaned data. (Code Execution Agent)
For each of the three steps, an LLM is used to perform the task. The LLM used is Mistral
