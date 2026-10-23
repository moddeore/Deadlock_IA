import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="Deadlock Lab | OS Dashboard", page_icon="🧠", layout="wide")

st.markdown("""
<style>
:root { --ink:#172033; --muted:#64748b; --line:#e2e8f0; --panel:#ffffff; --accent:#6d5ce8; --accent2:#14b8a6; }
.stApp { background: #f5f7fc; color: var(--ink); }
[data-testid="stHeader"] { background: rgba(245,247,252,.92); }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1450px; }
section[data-testid="stSidebar"] { background: #111827; border-right: 1px solid #263244; }
section[data-testid="stSidebar"] * { color: #e5e7eb; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label { padding: .45rem .55rem; border-radius: 9px; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: #263244; }
.hero { padding: 1.65rem 1.8rem; border-radius: 22px; background: linear-gradient(120deg,#4f46e5 0%,#6d5ce8 55%,#0faaa0 120%); color: white; margin-bottom: 1.35rem; box-shadow: 0 14px 34px rgba(79,70,229,.18); }
.hero h1 { margin: 0; font-size: 2.25rem; letter-spacing: -.04em; color: white; }
.hero p { margin: .5rem 0 0; color: #eef2ff; font-size: 1.02rem; }
.metric-card { min-height: 140px; padding: 1.15rem 1.2rem; border: 1px solid #e5e7eb; border-radius: 17px; background: white; box-shadow: 0 5px 18px rgba(31,41,55,.04); }
.metric-card h3 { color: #312e81; margin-top: 0; font-size: 1.15rem; }
.metric-card p { color: #64748b; margin-bottom: 0; }
.small-muted { color: #64748b; font-size: .9rem; }
h1, h2, h3 { letter-spacing: -.025em; }
[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; }
.stButton > button { border-radius: 10px; font-weight: 650; padding: .55rem 1rem; }
.stButton > button[kind="primary"] { background: #5b50df; border: 1px solid #5b50df; }
[data-testid="stAlert"] { border-radius: 12px; }
hr { border-color: #e2e8f0; }
</style>
<div class="hero"><h1>◈ Deadlock Lab</h1><p>OS Resource Studio · Explore safe allocation, resource requests, deadlock detection and recovery</p></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Navigation")
    page = st.radio("Choose module", ["Overview", "Banker's Algorithm", "Resource Request", "Deadlock Detection", "Prevention & Recovery", "Test Cases", "AI Usage Record"])
    st.divider()
    st.caption("OS Activity 2 · Deadlock Analysis")

# Classic example, with 5 processes and 3 resource types.
ALLOC0 = [[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
MAX0   = [[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]
AVAIL0 = [3,3,2]


def validate_matrices(alloc, maximum, available):
    if len(alloc) == 0 or len(alloc) != len(maximum): return "Allocation and Maximum must have the same non-zero number of processes."
    if any(len(r) != len(available) for r in alloc + maximum): return "Every row must have one value per resource type."
    if any(not isinstance(x, int) or x < 0 for row in alloc + maximum for x in row) or any(not isinstance(x, int) or x < 0 for x in available): return "Resource values must be non-negative integers."
    for i in range(len(alloc)):
        for j in range(len(available)):
            if alloc[i][j] > maximum[i][j]: return f"Invalid input: allocation exceeds maximum for P{i}, resource R{j}."
    return None


def need_matrix(alloc, maximum):
    return [[maximum[i][j] - alloc[i][j] for j in range(len(maximum[0]))] for i in range(len(alloc))]


def safety_check(alloc, maximum, available):
    n, m = len(alloc), len(available)
    need = need_matrix(alloc, maximum)
    work = available[:]
    finish = [False] * n
    sequence, trace = [], []
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                before = work[:]
                work = [work[j] + alloc[i][j] for j in range(m)]
                finish[i] = True
                sequence.append(f"P{i}")
                trace.append({"Process": f"P{i}", "Need": need[i][:], "Work before": before, "Work after": work[:]})
                changed = True
    return all(finish), sequence, need, trace, [f"P{i}" for i, done in enumerate(finish) if not done]


def fmt_matrix(matrix, prefix):
    return pd.DataFrame(matrix, index=[f"P{i}" for i in range(len(matrix))], columns=[f"R{j}" for j in range(len(matrix[0]))])


def render_state(alloc, maximum, available):
    st.subheader("Current system state")
    c1, c2, c3 = st.columns(3)
    c1.markdown("**Allocation**")
    c1.dataframe(fmt_matrix(alloc, "A"), use_container_width=True)
    c2.markdown("**Maximum**")
    c2.dataframe(fmt_matrix(maximum, "M"), use_container_width=True)
    c3.markdown("**Available**")
    c3.dataframe(pd.DataFrame([available], index=["Available"], columns=[f"R{j}" for j in range(len(available))]), use_container_width=True)


def state_editor(key="state"):
    st.caption("Edit the example values below if you want to test another system state.")
    n = st.number_input("Number of processes", 1, 8, 5, key=f"{key}_n")
    m = st.number_input("Number of resource types", 1, 5, 3, key=f"{key}_m")
    default_a = ALLOC0[:n] if n <= 5 and m == 3 else [[0]*m for _ in range(n)]
    default_max = MAX0[:n] if n <= 5 and m == 3 else [[1]*m for _ in range(n)]
    default_av = AVAIL0[:m] if m == 3 and n <= 5 else [1]*m
    st.markdown("**Allocation matrix**")
    a_df = pd.DataFrame(default_a, index=[f"P{i}" for i in range(n)], columns=[f"R{j}" for j in range(m)])
    a_df = st.data_editor(a_df, key=f"{key}_alloc", num_rows="fixed", use_container_width=True)
    st.markdown("**Maximum matrix**")
    mx_df = pd.DataFrame(default_max, index=[f"P{i}" for i in range(n)], columns=[f"R{j}" for j in range(m)])
    mx_df = st.data_editor(mx_df, key=f"{key}_max", num_rows="fixed", use_container_width=True)
    st.markdown("**Available vector**")
    av_df = pd.Data_editor if False else None
    av = []
    cols = st.columns(m)
    for j in range(m):
        av.append(int(cols[j].number_input(f"R{j}", min_value=0, value=int(default_av[j]), key=f"{key}_av{j}")))
    try:
        alloc = [[int(a_df.iloc[i,j]) for j in range(m)] for i in range(n)]
        maximum = [[int(mx_df.iloc[i,j]) for j in range(m)] for i in range(n)]
    except Exception:
        return None, None, None, "Matrix cells must contain integers."
    err = validate_matrices(alloc, maximum, av)
    return alloc, maximum, av, err

if page == "Overview":
    st.write("Use this dashboard to explore deadlock avoidance, detection, prevention and recovery with visible algorithm steps.")
    cols = st.columns(4)
    for col, title, desc in zip(cols, ["Safety analysis", "Request validation", "Deadlock detection", "Test coverage"], ["Need matrix and safe sequence", "Check Need, Available and safety", "Work/Finish detection method", "Six assignment scenarios"]):
        col.markdown(f'<div class="metric-card"><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
    st.subheader("Quick start")
    st.markdown("1. Open **Banker's Algorithm** and calculate the safe sequence.\n2. Try **Resource Request** to see granted and denied requests.\n3. Open **Deadlock Detection** to test a waiting-process scenario.\n4. Visit **Test Cases** to record actual outcomes for the assignment table.")
    st.info("Important: an unsafe state is not automatically a deadlock. Banker's Algorithm is an avoidance/safety method; deadlock detection is a separate procedure.")

elif page == "Banker's Algorithm":
    st.header("Banker's Algorithm — Safety Check")
    alloc, maximum, available, err = state_editor("banker")
    if err: st.error(err)
    elif st.button("Run safety algorithm", type="primary"):
        safe, seq, need, trace, unfinished = safety_check(alloc, maximum, available)
        st.markdown("**Need = Maximum − Allocation**")
        st.dataframe(fmt_matrix(need, "N"), use_container_width=True)
        if safe:
            st.success("SAFE STATE — a complete safe sequence exists.")
            st.markdown("**Safe sequence:** " + " → ".join(seq))
        else:
            st.warning("UNSAFE STATE — no complete safe sequence was found.")
            st.write("Processes unable to finish in this simulation:", ", ".join(unfinished))
        st.markdown("**Step-by-step Work vector**")
        if trace:
            st.dataframe(pd.DataFrame([{"Process": x["Process"], "Need": str(x["Need"]), "Work before": str(x["Work before"]), "Work after": str(x["Work after"])} for x in trace]), use_container_width=True)
        else: st.write("No process can complete with the currently available resources.")

elif page == "Resource Request":
    st.header("Resource Request Simulator")
    alloc, maximum, available, err = state_editor("request")
    if err: st.error(err)
    else:
        p = st.selectbox("Requesting process", [f"P{i}" for i in range(len(alloc))])
        pi = int(p[1:])
        request = []
        cols = st.columns(len(available))
        for j in range(len(available)):
            request.append(int(cols[j].number_input(f"Request for R{j}", min_value=0, value=0, key=f"req_r{j}")))
        if st.button("Evaluate request", type="primary"):
            need = need_matrix(alloc, maximum)
            if any(request[j] > need[pi][j] for j in range(len(request))):
                st.error("REQUEST DENIED: request exceeds the process's remaining Need. State unchanged.")
            elif any(request[j] > available[j] for j in range(len(request))):
                st.warning("NOT GRANTED NOW: request is within Need but exceeds Available resources. State unchanged.")
            else:
                a2 = [r[:] for r in alloc]; av2 = available[:]
                for j in range(len(request)):
                    a2[pi][j] += request[j]; av2[j] -= request[j]
                safe, seq, _, _, _ = safety_check(a2, maximum, av2)
                if safe:
                    st.success("REQUEST GRANTED in simulation: resulting state is safe.")
                    st.write("Safe sequence after request:", " → ".join(seq))
                    st.caption("This is a simulation; original input values are not permanently changed.")
                else:
                    st.error("REQUEST DENIED: it would leave the system unsafe. Original state restored.")

elif page == "Deadlock Detection":
    st.header("Deadlock Detection (separate from Banker's Algorithm)")
    st.write("This module uses the multi-instance detection algorithm with Allocation, Request and Available.")
    mode = st.radio("Scenario", ["Deadlock example", "No deadlock example"], horizontal=True)
    if mode == "Deadlock example":
        alloc = [[1,0],[0,1]]; request = [[0,1],[1,0]]; available = [0,0]
    else:
        alloc = [[1,0],[0,1]]; request = [[0,0],[0,0]]; available = [0,0]
    render_state(alloc, [[1,1],[1,1]], available)
    st.markdown("**Outstanding Request matrix**")
    st.dataframe(fmt_matrix(request, "Q"), use_container_width=True)
    if st.button("Run deadlock detection", type="primary"):
        work = available[:]
        finish = [sum(row) == 0 for row in alloc]
        steps=[]; changed=True
        while changed:
            changed=False
            for i in range(len(alloc)):
                if not finish[i] and all(request[i][j] <= work[j] for j in range(len(work))):
                    before=work[:]; work=[work[j]+alloc[i][j] for j in range(len(work))]
                    finish[i]=True; changed=True
                    steps.append({"Process":f"P{i}","Request":request[i],"Work before":before,"Work after":work[:]})
        stuck=[f"P{i}" for i,x in enumerate(finish) if not x]
        if stuck: st.error("DEADLOCK DETECTED among processes: " + ", ".join(stuck))
        else: st.success("NO DEADLOCK DETECTED: all processes can finish or hold no resources.")
        if steps: st.dataframe(pd.DataFrame(steps), use_container_width=True)
        st.caption("Assumption: the Request matrix represents each process's current outstanding resource request.")

elif page == "Prevention & Recovery":
    st.header("Deadlock Prevention & Recovery")
    st.subheader("Prevention policy")
    st.write("Choose a fixed resource-acquisition order. Every process must request R0 before R1, then R2, etc. This prevents circular wait when all processes follow the same order.")
    st.code("Rule: acquire resources only in ascending order (R0 → R1 → R2 → ...).", language="text")
    st.info("Trade-off: processes may wait longer, and resources may be held earlier than needed, reducing concurrency and utilization.")
    st.subheader("Recovery demonstration")
    st.write("Example: P0 holds R0 and waits for R1; P1 holds R1 and waits for R0. Terminating P1 releases R1 so P0 can proceed.")
    if st.button("Simulate terminating P1", type="primary"):
        st.success("Recovery applied in simulation: P1 terminated; its held resource R1 is released. P0 can now acquire R1 and continue.")
        st.caption("This is a conceptual simulation, not a real operating-system process termination.")

elif page == "Test Cases":
    st.header("Required Analytical Results — Test Cases")
    rows = [
        ["TC1", "Safe state", "Safe sequence found", "Banker's safety check completes all processes", "Pass when a full sequence is shown"],
        ["TC2", "Request exceeds Available", "Not granted immediately", "Request is within Need but exceeds Available; state unchanged", "Pass when no allocation changes"],
        ["TC3", "Request makes state unsafe", "Request denied", "Tentative allocation fails safety check; state restored", "Pass when no complete sequence exists"],
        ["TC4", "Deadlocked scenario", "Deadlock identified", "Detection algorithm leaves processes unfinished", "Pass when stuck processes are listed"],
        ["TC5", "Prevention policy", "Circular wait condition prevented", "Fixed resource order removes circular wait", "Pass when policy is explained"],
        ["TC6", "Boundary and invalid inputs", "Validation shown", "Zero resources accepted where valid; negative or inconsistent values rejected", "Pass when invalid values are flagged"],
    ]
    st.warning("These are expected outcomes. Run the relevant module and record the actual result you observe before submitting.")
    st.dataframe(pd.DataFrame(rows, columns=["Test Case", "System Condition", "Expected Result", "Analysis / Conclusion", "Verification"]), use_container_width=True, hide_index=True)
    st.subheader("Boundary input checklist")
    for item in ["Zero Available resources", "A process with zero remaining Need", "Invalid process identifier", "Negative request", "Allocation exceeding Maximum"]:
        st.checkbox(item, key="tc_"+item)

elif page == "AI Usage Record":
    st.header("AI Usage Record")
    st.write("Edit the entries to accurately reflect the tools your group actually used.")
    ai_df = pd.DataFrame([
        ["ChatGPT", "Understand deadlock concepts and draft algorithm logic", "Dashboard logic and explanatory text", "Group tested safety and request outcomes"],
        ["Streamlit", "Build the interactive dashboard interface", "Web-based dashboard", "Group checked each module"],
        ["Python", "Implement and run the algorithms", "Source code", "Group reviewed results and edge cases"],
    ], columns=["AI Tool / Software", "Purpose", "Output Generated", "Student Verification"])
    st.data_editor(ai_df, num_rows="dynamic", use_container_width=True, key="ai_record")
    st.caption("Do not claim a tool was used unless your group actually used it. Verify all algorithm results independently.")

st.divider()
st.caption("Deadlock Lab · Educational simulator · Review and test outputs before submission.")
