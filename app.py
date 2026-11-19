import os
import streamlit as st
from dotenv import load_dotenv
from rag import SchemeRAG
from agents import SchemeResearchAgent, EligibilityAgent, DocumentAgent, GuidanceAgent

load_dotenv()
st.set_page_config(page_title="Government Scheme AI Assistant", page_icon="🏛️", layout="wide")
st.title("🏛️ AI Agent for Government Scheme Eligibility and Application Verification")
st.caption("RAG-powered preliminary guidance using scheme documents supplied by the project administrator.")

nexus_api_key = os.getenv("NEXUS_API_KEY", "").strip()
nexus_base_url = os.getenv("NEXUS_BASE_URL", "").strip().rstrip("/")
if nexus_api_key and not nexus_base_url:
    st.error("NEXUS_BASE_URL must be set when using NEXUS_API_KEY.")
    st.stop()

api_key = nexus_api_key or os.getenv("OPENAI_API_KEY", "").strip()
base_url = None
if nexus_api_key:
    base_url = nexus_base_url if nexus_base_url.endswith("/v1") else f"{nexus_base_url}/v1"
    model = os.getenv("NEXUS_MODEL", "nova-micro").strip()
    embedding_model = os.getenv("NEXUS_EMBEDDING_MODEL", "text-embedding-3-small").strip()
else:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

with st.sidebar:
    st.header("Knowledge base")
    st.write("Upload official scheme PDFs or text files. The app indexes them for retrieval.")
    uploaded = st.file_uploader("Upload scheme documents", type=["pdf", "txt", "md"], accept_multiple_files=True)
    if st.button("Index uploaded documents", disabled=not uploaded):
        if not api_key:
            st.error("Add NEXUS_API_KEY or OPENAI_API_KEY to your .env file first.")
        else:
            rag = SchemeRAG(api_key, model, embedding_model, base_url)
            count = rag.add_uploaded_files(uploaded)
            st.success(f"Indexed {count} document chunk(s).")
    st.divider()
    st.caption("Use current official documents only. This tool provides preliminary guidance, not an official eligibility decision.")

if not api_key:
    st.warning("API key not configured. Add Nexus or OpenAI settings to your .env file.")
    st.stop()

rag = SchemeRAG(api_key, model, embedding_model, base_url)
research_agent = SchemeResearchAgent(rag, api_key, model, base_url)
eligibility_agent = EligibilityAgent(api_key, model, base_url)
document_agent = DocumentAgent(api_key, model, base_url)
guidance_agent = GuidanceAgent(api_key, model, base_url)

tab1, tab2, tab3 = st.tabs(["Find schemes", "Check a scheme", "Application guidance"])

with tab1:
    st.subheader("Find potentially relevant schemes")
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            state = st.text_input("State / Union Territory", "Tamil Nadu")
            age = st.number_input("Age", min_value=0, max_value=120, value=25)
            gender = st.selectbox("Gender (if relevant to scheme)", ["Prefer not to say", "Female", "Male", "Other"])
            category = st.selectbox("Social category (optional)", ["Not provided", "General", "SC", "ST", "OBC", "Other"])
        with c2:
            annual_income = st.number_input("Annual family income (₹)", min_value=0, value=0, step=10000)
            occupation = st.text_input("Occupation")
            rural_urban = st.selectbox("Area", ["Not provided", "Rural", "Urban"])
            purpose = st.text_area("What support are you looking for?", placeholder="For example: education scholarship, housing, business loan...")
        submitted = st.form_submit_button("Find matching schemes")
    if submitted:
        profile = {"state": state, "age": age, "gender": gender, "social_category": category,
                   "annual_family_income_inr": annual_income, "occupation": occupation,
                   "area": rural_urban, "support_needed": purpose}
        with st.spinner("Research agent is searching the indexed official documents..."):
            result = research_agent.find_schemes(profile)
        st.markdown(result)

with tab2:
    st.subheader("Preliminary eligibility check")
    scheme_name = st.text_input("Scheme name")
    profile_json = st.text_area("Applicant details (plain language)", placeholder="State, age, family income, occupation, category, etc.")
    if st.button("Check preliminary eligibility"):
        if not scheme_name or not profile_json:
            st.error("Enter both the scheme name and applicant details.")
        else:
            with st.spinner("Retrieving scheme rules and checking the supplied profile..."):
                context = rag.retrieve(f"{scheme_name} eligibility criteria age income residence category exclusions documents")
                result = eligibility_agent.check(scheme_name, profile_json, context)
            st.markdown(result)

with tab3:
    st.subheader("Missing documents and application steps")
    scheme_for_docs = st.text_input("Scheme name for document check")
    applicant_docs = st.text_area("Documents currently available", placeholder="Aadhaar, income certificate, bank passbook...")
    if st.button("Verify documents and get steps"):
        if not scheme_for_docs:
            st.error("Enter a scheme name.")
        else:
            with st.spinner("Document agent is checking the retrieved requirements..."):
                context = rag.retrieve(f"{scheme_for_docs} required documents proof certificates application process official")
                doc_result = document_agent.verify(scheme_for_docs, applicant_docs, context)
                st.markdown("### Document verification")
                st.markdown(doc_result)
                guidance = guidance_agent.steps(scheme_for_docs, context)
                st.markdown("### Application guidance")
                st.markdown(guidance)

st.divider()
st.caption("Important: Eligibility results are estimates based only on indexed material and the details entered. Confirm all requirements, deadlines, and application links with the relevant official department.")
