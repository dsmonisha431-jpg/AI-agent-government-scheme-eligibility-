from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class BaseAgent:
    def __init__(self, api_key, model, base_url=None):
        self.llm = ChatOpenAI(model=model, temperature=0, api_key=api_key, base_url=base_url)

    def ask(self, system, user):
        response = self.llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
        return response.content

class SchemeResearchAgent(BaseAgent):
    def __init__(self, rag, api_key, model, base_url=None):
        super().__init__(api_key, model, base_url)
        self.rag = rag

    def find_schemes(self, profile):
        query = "Government scheme eligibility benefits application criteria for " + str(profile)
        context = self.rag.retrieve(query, k=8)
        return self.ask(
            "You are a scheme research agent. Use ONLY the supplied retrieved context. "
            "List potentially relevant schemes, why they may match, important conditions, and source filenames/pages. "
            "If evidence is absent, say so. Never invent a scheme, benefit, deadline, URL, or eligibility rule. "
            "Clearly label results as preliminary, not an official decision.",
            f"Applicant profile:\n{profile}\n\nRetrieved official-document excerpts:\n{context}"
        )

class EligibilityAgent(BaseAgent):
    def __init__(self, api_key, model, base_url=None):
        super().__init__(api_key, model, base_url)

    def check(self, scheme, profile, context):
        return self.ask(
            "You are an eligibility verification agent. Compare each stated criterion with applicant details. "
            "Return a table with criterion, evidence from source, applicant detail, status (appears met/not met/unknown). "
            "Do not assume missing details. Conclude: potentially eligible, likely not eligible, or insufficient information. "
            "Cite source filename/page from context. State this is not an official decision.",
            f"Scheme: {scheme}\nApplicant details:\n{profile}\n\nRetrieved context:\n{context}"
        )

class DocumentAgent(BaseAgent):
    def __init__(self, api_key, model, base_url=None):
        super().__init__(api_key, model, base_url)

    def verify(self, scheme, available_docs, context):
        return self.ask(
            "You are a document verification agent. Extract only document requirements explicitly present in context. "
            "Compare them with the applicant's available documents. Categorize as available, missing, or unclear. "
            "Do not claim a document is mandatory unless the source says so. Cite source filename/page. "
            "If no document list was retrieved, say that clearly.",
            f"Scheme: {scheme}\nApplicant documents:\n{available_docs or 'Not provided'}\n\nRetrieved context:\n{context}"
        )

class GuidanceAgent(BaseAgent):
    def __init__(self, api_key, model, base_url=None):
        super().__init__(api_key, model, base_url)

    def steps(self, scheme, context):
        return self.ask(
            "You are an application guidance agent. Give numbered application steps only when supported by retrieved context. "
            "Include official portal/office details only if explicitly present in context. Do not fabricate links, dates, fees, "
            "or processing times. If the source lacks steps, provide a short checklist of what the user should confirm "
            "with the responsible government department.",
            f"Scheme: {scheme}\n\nRetrieved context:\n{context}"
        )
